from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading

import pytest

from pricinglibrary_rag.learner_cli import Client, CliFailure, strict_json, token_value


def test_transport_retries_only_explicitly_safe_operations_and_never_follows_redirects():
    counters={"get":0,"post":0,"target":0}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_):pass
        def send(self,status,value):
            content=json.dumps(value).encode();self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(content)));self.end_headers();self.wfile.write(content)
        def do_GET(self):
            if self.path=="/redirect":
                self.send_response(302);self.send_header("Location","/target");self.end_headers();return
            if self.path=="/target":counters["target"]+=1;self.send(200,{"unexpected":True});return
            counters["get"]+=1;self.send(503,{"detail":"Temporary test failure"}) if counters["get"]==1 else self.send(200,{"ready":True})
        def do_POST(self):
            counters["post"]+=1;self.send(503,{"detail":"Explicit transport-only failure"})
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    client=Client(f"http://127.0.0.1:{server.server_port}","fixture-not-a-real-token",timeout=2,retries=1)
    try:
        assert client.call("/transient")=={"ready":True} and counters["get"]==2
        with pytest.raises(CliFailure):client.call("/unsafe","POST",{"message":"Do not duplicate"})
        assert counters["post"]==1
        with pytest.raises(CliFailure):client.call("/redirect")
        assert counters["target"]==0
    finally:server.shutdown();server.server_close();thread.join(timeout=3)


@pytest.mark.parametrize("base",["http://external.example","https://user:password@api.example","https://api.example?token=secret","file:///tmp/x"])
def test_unsafe_api_addresses_are_rejected_without_echoing_credentials(base):
    with pytest.raises(CliFailure) as error:Client(base)
    assert "password" not in error.value.message and "secret" not in error.value.message


@pytest.mark.parametrize("value",['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}'])
def test_noncanonical_json_is_rejected(value):
    with pytest.raises(ValueError):strict_json(value)


def test_token_files_are_bounded_and_never_allow_header_injection(tmp_path,monkeypatch):
    path=tmp_path/"session.private.json";path.write_text('{"access_token":"a.valid.fixture"}',encoding="utf-8")
    monkeypatch.setenv("TPL_ACCESS_TOKEN","another.fixture")
    assert token_value(str(path))=="a.valid.fixture"
    monkeypatch.setenv("TPL_ACCESS_TOKEN","bad\r\nX-Injected: value")
    with pytest.raises(CliFailure):token_value()

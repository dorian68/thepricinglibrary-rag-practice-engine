"""Read all real published EN variants through fresh signed HTTP and CLI.

Private course documents must already be mounted and accepted. This probe uses
explicit technical identities/entitlements in a temporary store, not real
Supabase customers, purchases or a legal source-rights clearance.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import tempfile
import threading
import time
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from pricinglibrary_rag.api import COURSE_SCRIPT_FILES,create_app,_public_course_markdown
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.course_publication import accepted_english_course
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.security import mint_session_token
import uvicorn


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir",default=str(ROOT/"pricinglibrary_rag/course_scripts"))
    parser.add_argument("--report",default=str(ROOT.parents[1]/"reports/product-hardening-2026-11-14/english-published-http-cli.json"))
    args=parser.parse_args()
    directory=Path(args.dir).resolve()
    published={course_id:accepted_english_course(directory,filename) for course_id,filename in COURSE_SCRIPT_FILES.items()}
    if len(published)!=12 or not all(published.values()): raise RuntimeError("Twelve hash-accepted private EN variants are required")
    logging.disable(logging.CRITICAL)
    temporary_root=ROOT/".tmp";temporary_root.mkdir(exist_ok=True)
    report={"schema":"tpl.english-course.published-smoke.v1","verdict":"PASS",
        "scope":"Fresh HTTP and CLI with real JWT verification and technical fixture identities/plans/rights flag; no external Supabase login, purchase or legal clearance is attested",
        "source_corpus_access":"none; reads the already reviewed private course documents",
        "courses":[]}
    with tempfile.TemporaryDirectory(prefix="english-publish-",dir=temporary_root) as temporary:
        temp=Path(temporary).resolve()
        assert temp.is_relative_to(temporary_root.resolve())
        secret=secrets.token_urlsafe(48)
        settings=Settings(data_dir=temp,db_path=temp/"technical.sqlite3",embedding_backend="local-hashing",embedding_dim=64,
            sentence_transformer_model=None,llm_provider="template",openai_api_key=None,openai_model="unused",openai_base_url=None,
            openai_timeout_seconds=1,openai_max_retries=0,ollama_url="http://127.0.0.1:1",ollama_model="unused",
            transformers_model_path=None,chunk_target_chars=700,chunk_overlap_chars=80,max_context_chunks=4,
            environment="production",auth_token_secret=secret,api_key="fixture-member-"+secrets.token_hex(24),
            operator_api_key="fixture-operator-"+secrets.token_hex(24),rate_limit_per_min=10000,
            course_scripts_dir=directory,source_rights_cleared=True)
        services=build_services(settings)
        tokens={}
        for account,plan in (("free",None),("student","student"),("pro","pro")):
            subject="english-smoke-"+account
            email=subject+"@isolated.test"
            if plan:services.store.upsert_entitlement(email,plan,user_id=subject,status="active",source="technical-published-course-fixture")
            tokens[account]=mint_session_token(secret,user_id=subject,email=email,expires_at=int(time.time())+600,role="member")
        app=create_app(services)
        sock=socket.socket();sock.bind(("127.0.0.1",0));sock.listen(128)
        origin=f"http://127.0.0.1:{sock.getsockname()[1]}"
        server=uvicorn.Server(uvicorn.Config(app,log_level="critical",access_log=False))
        thread=threading.Thread(target=server.run,kwargs={"sockets":[sock]},daemon=True)
        thread.start()
        deadline=time.monotonic()+15
        while not server.started and thread.is_alive() and time.monotonic()<deadline:time.sleep(.01)
        if not server.started:raise RuntimeError("Fresh course API did not start")
        empty_token=temp/"anonymous-token.private";empty_token.write_text("",encoding="utf-8")
        base_env={k:v for k,v in os.environ.items() if k.upper() in {"PATH","SYSTEMROOT","WINDIR","TEMP","TMP","USERPROFILE","LOCALAPPDATA","APPDATA","COMSPEC","PATHEXT"}}
        base_env["PYTHONIOENCODING"]="utf-8"
        def cli(account,*command,expected=0):
            env=dict(base_env)
            if account:env["TPL_ACCESS_TOKEN"]=tokens[account]
            else:env["TPL_TOKEN_FILE"]=str(empty_token)
            result=subprocess.run([sys.executable,"-m","pricinglibrary_rag.learner_cli","--api",origin,"--retries","0",*command],
                cwd=ROOT,env=env,capture_output=True,text=True,encoding="utf-8",timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
            if result.returncode!=expected:raise RuntimeError(f"CLI {command[0:2]} returned {result.returncode}, expected {expected}")
            if any(token in result.stdout+result.stderr for token in tokens.values()):raise RuntimeError("Credential appeared in CLI output")
            value=json.loads(result.stdout)
            return value.get("data")
        try:
            catalog=cli(None,"courses","list")
            assert len(catalog)==12 and all("en" in row["available_languages"] for row in catalog)
            identity=cli("pro","auth","whoami")
            assert identity["user_id"]=="english-smoke-pro" and identity["role"]=="member"
            for course_id,filename in COURSE_SCRIPT_FILES.items():
                cli(None,"courses","read",course_id,"--language","en",expected=3)
                cli("free","courses","read",course_id,"--language","en",expected=4)
                if course_id in {"exotics","monte-carlo","stochastic","structured-products"}:
                    cli("student","courses","read",course_id,"--language","en",expected=4)
                result=cli("pro","courses","read",course_id,"--language","en")
                content=result["content"]
                assert content==_public_course_markdown(published[course_id])
                assert "## Written course" in content and "## Cours redige" not in content
                assert "Source Appendix" not in content and not re.search(r"\[S\d+\]",content)
                assert len(re.findall(r"^Answer: \*\*[A-E]\*\*",content,re.M))==5
                request=Request(origin+f"/courses/{course_id}/script?language=en",headers={"Authorization":"Bearer "+tokens["pro"]})
                with urlopen(request,timeout=30) as response:
                    assert response.headers["Content-Language"]=="en"
                    assert "no-store" in response.headers["Cache-Control"]
                    assert response.read().decode("utf-8")==content
                report["courses"].append({"course_id":course_id,"slug":filename[:-3],"raw_sha256":hashlib.sha256((directory/"en"/filename).read_bytes()).hexdigest(),
                    "content_language":"en","anonymous_denied":True,"free_denied":True,"member_pro_read":True,
                    "lessons":len(re.findall(r"^### Lesson \d+ -",content,re.M)),"quiz_questions":5,"private_metadata_absent":True})
        finally:
            server.should_exit=True
            thread.join(timeout=15)
            sock.close()
            if thread.is_alive():raise RuntimeError("Fresh course API did not shut down")
            # sqlite connection/cursor cycles may otherwise delay finalisation
            # until after TemporaryDirectory cleanup on Windows.
            gc.collect()
    target=Path(args.report).resolve();target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"verdict":"PASS","fresh_http_and_cli":True,"courses":len(report["courses"]),"signed_role":"member","report":str(target)}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())

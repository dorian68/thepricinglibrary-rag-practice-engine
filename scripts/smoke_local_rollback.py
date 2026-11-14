"""Exercise a real local SQLite backup/restore across API restarts.

This validates the repository's single-host rollback mechanics with a temporary
database and the real HTTP acceptance probe. It is deliberately not Docker,
registry, Stripe, Supabase or public rollback evidence.
"""

from __future__ import annotations

import gc
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_ROOT.parent
sys.path.insert(0, str(BACKEND_ROOT))

from smoke_local_deployment import (  # noqa: E402
    LOCAL_AUTH_SECRET,
    LOCAL_USER_ID,
    PROBE,
    STARTER_ROOT,
    _free_port,
    _wait_for_health,
    local_fixture_environment,
)
from pricinglibrary_rag.security import mint_session_token  # noqa: E402
from pricinglibrary_rag.storage import LocalStore  # noqa: E402


PRODUCT_ID = "market-finance-starter-kit"


def _start_api(data_dir: Path, bundle: Path, manifest: Path) -> tuple[subprocess.Popen[bytes], dict[str, str], str]:
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = local_fixture_environment(data_dir, bundle, manifest)
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "pricinglibrary_rag.api:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=BACKEND_ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _wait_for_health(base_url, process)
    return process, env, base_url


def _stop_api(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)
    gc.collect()
    time.sleep(0.15)


def _token() -> str:
    return mint_session_token(
        LOCAL_AUTH_SECRET,
        user_id=LOCAL_USER_ID,
        email="local-http-entitled@example.invalid",
        expires_at=int(time.time()) + 600,
    )


def _seed_entitlement(db_path: Path) -> None:
    store = LocalStore(db_path)
    store.upsert_product_entitlement(LOCAL_USER_ID, PRODUCT_ID, status="active", source="local-rollback-smoke")
    del store
    gc.collect()


def _probe(base_url: str, env: dict[str, str], output_path: Path) -> tuple[int, dict]:
    probe_env = env.copy()
    probe_env["TPL_STAGING_ACCESS_TOKEN"] = _token()
    result = subprocess.run(
        [
            sys.executable,
            str(PROBE),
            "--base-url",
            base_url,
            "--allow-http-local",
            "--require-entitled",
            "--json-out",
            str(output_path),
        ],
        cwd=BACKEND_ROOT,
        env=probe_env,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    report = json.loads(output_path.read_text(encoding="utf-8"))
    return result.returncode, report


def _backup_database(source: Path, destination: Path) -> None:
    source_conn = sqlite3.connect(source)
    destination_conn = sqlite3.connect(destination)
    try:
        source_conn.backup(destination_conn)
    finally:
        destination_conn.close()
        source_conn.close()
        gc.collect()


def main() -> int:
    bundle = STARTER_ROOT / "release" / "starter-kit-v1.0.0.zip"
    manifest = STARTER_ROOT / "release" / "manifest.json"
    if not bundle.is_file() or not manifest.is_file():
        print("LOCAL ROLLBACK SMOKE FAIL: verified Starter Kit artifact is missing")
        return 1

    process: subprocess.Popen[bytes] | None = None
    stage = "initialisation"
    try:
        with tempfile.TemporaryDirectory(prefix="tpl-local-rollback-", ignore_cleanup_errors=True) as raw_dir:
            data_dir = Path(raw_dir)
            db_path = data_dir / "pricinglibrary_rag.sqlite3"
            backup_path = data_dir / "rollback-backup.sqlite3"
            stage = "démarrage initial"
            _process, env, base_url = _start_api(data_dir, bundle, manifest)
            process = _process
            stage = "seed entitlement"
            _seed_entitlement(db_path)
            stage = "probe initial"
            initial_code, initial_report = _probe(base_url, env, data_dir / "initial.json")
            if initial_code != 0 or initial_report.get("failed_checks") != 0:
                print("LOCAL ROLLBACK SMOKE FAIL: initial entitled acceptance failed")
                return 1
            stage = "arrêt initial"
            _stop_api(process)
            process = None

            stage = "backup SQLite"
            _backup_database(db_path, backup_path)
            stage = "corruption temporaire"
            conn = sqlite3.connect(db_path)
            try:
                conn.execute("DELETE FROM product_entitlements")
                conn.commit()
            finally:
                conn.close()
            gc.collect()
            stage = "restart dégradé"
            process, env, base_url = _start_api(data_dir, bundle, manifest)
            stage = "probe dégradé"
            degraded_code, degraded_report = _probe(base_url, env, data_dir / "degraded.json")
            degraded_names = {
                str(item.get("name"))
                for item in degraded_report.get("checks", [])
                if item.get("pass") is False
            }
            if degraded_code == 0 or not ({"entitled-manifest", "entitled-download"} & degraded_names):
                print("LOCAL ROLLBACK SMOKE FAIL: entitlement loss was not detected")
                return 1
            stage = "arrêt dégradé"
            _stop_api(process)
            process = None

            stage = "suppression sidecars"
            for suffix in ("-wal", "-shm"):
                sidecar = Path(f"{db_path}{suffix}")
                if sidecar.exists():
                    sidecar.unlink()
            stage = "restauration SQLite"
            shutil.copy2(backup_path, db_path)
            stage = "restart restauré"
            process, env, base_url = _start_api(data_dir, bundle, manifest)
            stage = "probe restauré"
            restored_code, restored_report = _probe(base_url, env, data_dir / "restored.json")
            if restored_code != 0 or restored_report.get("failed_checks") != 0:
                print("LOCAL ROLLBACK SMOKE FAIL: restored entitled acceptance failed")
                return 1
            print(
                "LOCAL ROLLBACK SMOKE PASS: SQLite backup/restore, API restart and "
                "entitled SHA-256 download survived the local rollback drill"
            )
            return 0
    except (OSError, RuntimeError, sqlite3.Error, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"LOCAL ROLLBACK SMOKE FAIL: {type(exc).__name__} during {stage}")
        return 1
    finally:
        if process is not None:
            _stop_api(process)


if __name__ == "__main__":
    raise SystemExit(main())

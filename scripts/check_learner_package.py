"""Build/install the public wheel in an isolated prefix, then test outside checkout.

The prefix reuses this interpreter's dependencies; it never installs globally.
Private course scripts and corpus files are intentionally excluded from staging.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT.parents[1] / "reports" / "product-hardening-2026-11-14" / "cli-package-proof"
FLAGS = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def run(args, *, cwd, env=None, timeout=180):
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True,
                            encoding="utf-8", timeout=timeout, creationflags=FLAGS)
    if result.returncode:
        raise RuntimeError(f"Package check failed ({result.returncode}): "
                           + result.stdout[-6000:] + result.stderr[-6000:])
    return result.stdout


def main():
    PROOF.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="build-", dir=PROOF) as temporary:
        work = Path(temporary)
        stage = work / "source"
        stage.mkdir()
        shutil.copy2(ROOT / "pyproject.toml", stage / "pyproject.toml")
        shutil.copytree(ROOT / "pricinglibrary_rag", stage / "pricinglibrary_rag",
                        ignore=shutil.ignore_patterns("course_scripts", "__pycache__", "*.pyc"))
        wheels = PROOF / "wheels"
        wheels.mkdir(exist_ok=True)
        run([sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "--wheel-dir", str(wheels)], cwd=stage)
        wheel = wheels / "pricinglibrary_rag_backend-0.1.0-py3-none-any.whl"
        with zipfile.ZipFile(wheel) as archive:
            entries = archive.namelist()
            assert not any("course_scripts/" in name or name.endswith(".sqlite3") for name in entries)
            assets = "pricinglibrary_rag/learning_assets/"
            assert len(json.loads(archive.read(assets + "practice_exercises.json"))["exercises"]) == 14
            assert len(json.loads(archive.read(assets + "survival_questions.json"))["questions"]) == 20
            assert len(json.loads(archive.read(assets + "notebook_catalog.json"))["notebooks"]) == 2
            for name in ("black_scholes_intro", "barrier_down_out"):
                assert f"pricinglibrary_rag/builtin_notebooks/{name}.py" in entries
            assert "pricinglibrary_rag/js/modelCalibration.mjs" in entries
            entrypoint = next(name for name in entries if name.endswith(".dist-info/entry_points.txt"))
            assert "tpl = pricinglibrary_rag.learner_cli:main" in archive.read(entrypoint).decode()
        prefix = PROOF / "install-final"
        run([sys.executable, "-m", "pip", "install", "--no-deps", "--force-reinstall", "--prefix", str(prefix), str(wheel)], cwd=work)
        site = prefix / ("Lib/site-packages" if os.name == "nt" else f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages")
        launcher = prefix / ("Scripts/tpl.exe" if os.name == "nt" else "bin/tpl")
        env = dict(os.environ)
        env["PYTHONPATH"] = str(site)
        env.pop("TPL_ACCESS_TOKEN", None)
        env.pop("TPL_TOKEN_FILE", None)
        coverage = json.loads(run([str(launcher), "--api", "http://127.0.0.1:1", "coverage"], cwd=work, env=env))["data"]
        code = r'''
import json, sys
from pathlib import Path
from pricinglibrary_rag import api, cli_auth, course_publication, learning_workflows, learner_cli, practice_references
from pricinglibrary_rag.config import Settings
from pricinglibrary_rag.factory import build_services
from pricinglibrary_rag.builtin_notebooks.black_scholes_intro import run
from pricinglibrary_rag.canonical_tools import run_canonical_tool, tool_example
from fastapi.testclient import TestClient
prefix = Path(sys.argv[1]).resolve()
for module in (api, cli_auth, course_publication, learning_workflows, learner_cli, practice_references):
    assert Path(module.__file__).resolve().is_relative_to(prefix), module.__file__
data = Path(sys.argv[2]); data.mkdir()
settings = Settings(data_dir=data, db_path=data/'isolated.sqlite3', embedding_backend='local-hashing',
    embedding_dim=64, sentence_transformer_model=None, llm_provider='template', openai_api_key=None,
    openai_model='unused', openai_base_url=None, openai_timeout_seconds=1, openai_max_retries=0,
    ollama_url='http://127.0.0.1:1', ollama_model='unused', transformers_model_path=None,
    chunk_target_chars=700, chunk_overlap_chars=80, max_context_chunks=4, environment='production',
    auth_token_secret='package-check-fixture-not-a-real-secret-' * 2,
    api_key='package-member-fixture-' * 3, operator_api_key='package-operator-fixture-' * 3,
    rate_limit_per_min=100)
app = api.create_app(build_services(settings))
paths = {route.path for route in app.routes}
assert '/learning/catalog' in paths and '/learner/catalog' in paths
anonymous = TestClient(app).get('/learning/catalog')
assert anonymous.status_code == 401, (anonymous.status_code, anonymous.text)
assert len(learning_workflows.BANK) == 20 and len(learning_workflows.PRACTICE_EXERCISES) == 14
assert len(learning_workflows.NOTEBOOKS) == 2 and isinstance(run(), dict)
assert len(practice_references.list_reference_ids()) == 14
reference = practice_references.run_reference('iv-newton')
assert isinstance(reference, dict) and reference
assert practice_references.export_reference('iv-newton', format='ipynb')
assert run_canonical_tool('bs-pricer', tool_example('bs-pricer'))['selected']['unitPrice'] > 0
calibration = run_canonical_tool('calib', tool_example('calib'))
assert isinstance(calibration, dict) and calibration
print(json.dumps({'create_app_outside_checkout':True, 'learning_assets_loaded':True,
    'anonymous_learning_rejected':True, 'builtin_notebook_executed':True,
    'packaged_canonical_bs_and_node_calibration_executed':True,
    'packaged_reference_executed_and_exported':True,
    'counts':{'practice_exercises':14,'practice_references':14,'survival_questions':20,'notebooks':2}}))
'''
        runtime = json.loads(run([sys.executable, "-c", code, str(site), str(work / "runtime")], cwd=work, env=env, timeout=90))
        proof = {"verdict": "PASS", "wheel": wheel.name,
                 "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
                 "paid_course_files_packaged": False, "dependency_environment": "current interpreter; isolated install prefix",
                 "entrypoint": "tpl", "entrypoint_started_outside_checkout": True, "catalog": coverage, **runtime}
        target = PROOF.parent / "cli-package-proof.json"
        target.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(proof, ensure_ascii=False))


if __name__ == "__main__":
    main()

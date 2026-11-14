"""Reproduce English source generation, the strict gate and focused tests.

No publication occurs. The corpus remains read-only and drafts stay private.
"""
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir",default=str(ROOT/"generated_english_courses"))
    parser.add_argument("--corpus",default=str(ROOT/"data/pricinglibrary_rag.sqlite3"))
    parser.add_argument("--existing",action="store_true",help="Audit existing drafts rather than regenerate")
    args=parser.parse_args()
    if not args.existing:
        result=subprocess.run([sys.executable,"-u","scripts/generate_english_courses.py","--corpus",args.corpus,
            "--output-dir",args.dir],cwd=ROOT)
        if result.returncode: return result.returncode
    sys.path.insert(0,str(ROOT/"scripts"))
    import audit_course_quality
    audit_course_quality.DEFAULT_CORPUS_DB=Path(args.corpus).resolve()
    report=audit_course_quality.audit_dir(Path(args.dir).resolve(),98)
    print(json.dumps({"step":"strict_english_gate","status":report["section_gate"],
        "courses":report["courses_audited"],"passed":report.get("courses_passing_gate",0),"threshold":98,
        "failures":[{"slug":c["slug"],"issues":c["issues"]} for c in report["per_course"] if c["gate"]!="PASS"]}))
    if report["section_gate"]!="PASS": return 1
    return subprocess.call([sys.executable,"-m","pytest","-q","tests/test_english_courses.py",
        "--basetemp=.pytest_tmp_english_course_smoke","--tb=short"],cwd=ROOT)


if __name__=="__main__":
    raise SystemExit(main())

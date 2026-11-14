"""Run real CLI processes against the isolated, signed HTTP test server.

No Supabase login/payment/desktop is simulated as a commercial result: JWTs and
entitlements are explicit technical fixtures in the test's temporary database.
"""
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
if __name__=="__main__":
    raise SystemExit(subprocess.call([sys.executable,"-m","pytest","-q","tests/test_learner_cli.py","tests/test_learner_transport.py","tests/test_cli_auth.py","tests/test_course_publication.py",
                                    "--basetemp=.pytest_tmp_learner_cli_smoke","--tb=short"],cwd=root))

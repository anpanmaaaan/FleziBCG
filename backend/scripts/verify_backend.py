"""
BACKEND-QA-BASELINE-01: Backend verification script.

Runs the canonical backend health and QA checks in order:

  1. Backend import check
  2. DB direct connectivity (pg_isready + SELECT 1 via psycopg)
  3. Focused testenv tests (test_testenv_db_safety + test_testenv_db_connectivity_contract)
  4. Full backend pytest suite

Usage (from repo root, WSL / Linux / Codespaces):

    cd backend
    PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 scripts/verify_backend.py

    # Testenv-only (faster, no full suite):
    cd backend
    PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 scripts/verify_backend.py --testenv-only

If DB is unreachable the script prints the remediation hint and exits non-zero.
Passwords are never printed.

IMPORTANT: This script uses the DEV/TEST Docker DB only.
           It must NOT be run against a production database.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_COMPOSE_FILE = "docker/docker-compose.db.yml"
_COMPOSE_DB_SERVICE = "db"

_DEV_DB_START_HINT = (
    "  To start the dev/test DB:\n"
    f"    docker compose -f {_COMPOSE_FILE} up -d {_COMPOSE_DB_SERVICE}\n"
    f"  Compose file: {_COMPOSE_FILE}  (service: {_COMPOSE_DB_SERVICE}, port: 5432)\n"
    "  Backend env:  backend/.env  (POSTGRES_HOST=localhost, POSTGRES_PORT=5432)\n"
    "  If the container exists but port is not bound, use --force-recreate:\n"
    f"    docker compose -f {_COMPOSE_FILE} up -d --force-recreate {_COMPOSE_DB_SERVICE}"
)


def _mask_url(url: str) -> str:
    """Return url with password replaced by ***. Never prints secrets."""
    import re

    return re.sub(r"(://[^:@/]+:)[^@]+(@)", r"\1***\2", url)


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _print_results(results: list[Check]) -> None:
    print()
    for check in results:
        status = "PASS" if check.passed else "FAIL"
        print(f"  [{status}] {check.name}")
        if not check.passed and check.detail:
            for line in check.detail.splitlines():
                print(f"         {line}")
    print()


# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------


def check_backend_import() -> Check:
    """Verify app.main imports without error."""
    try:
        import app.main  # noqa: F401

        return Check("Backend import (app.main)", True, "")
    except Exception as exc:
        return Check("Backend import (app.main)", False, f"{type(exc).__name__}: {exc}")


def check_db_connectivity() -> Check:
    """Probe DB via psycopg. Returns False with remediation hint if unreachable."""
    try:
        from app.config.settings import settings

        raw_url = settings.database_url or ""

        # Strip SQLAlchemy dialect qualifier for psycopg.connect() (libpq URI format).
        url = raw_url
        for prefix in ("postgresql+psycopg://", "postgres+psycopg://"):
            if raw_url.startswith(prefix):
                url = "postgresql://" + raw_url[len(prefix) :]
                break

        import psycopg

        psycopg.connect(url, connect_timeout=3).close()
        return Check(
            f"DB connectivity ({_mask_url(raw_url)})",
            True,
            "",
        )
    except Exception as exc:
        try:
            from app.config.settings import settings as _s

            raw_url = _s.database_url or "<url-unavailable>"
        except Exception:
            raw_url = "<url-unavailable>"

        detail = (
            f"{type(exc).__name__}: {exc}\n"
            f"{_DEV_DB_START_HINT}"
        )
        return Check(
            f"DB connectivity ({_mask_url(raw_url)})",
            False,
            detail,
        )


def check_ruff_lint() -> Check:
    """Run ruff check . and return pass/fail. Requires ruff in PATH or PYTHONPATH."""
    cmd = [sys.executable, "-m", "ruff", "check", "."]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    passed = result.returncode == 0
    if passed:
        return Check("Ruff lint (ruff check .)", True, "")
    # Find summary line
    summary = ""
    for line in reversed(output.splitlines()):
        if "error" in line or "warning" in line or "All checks" in line:
            summary = line.strip()
            break
    return Check("Ruff lint (ruff check .)", False, summary or output[:200])


def check_pytest(args: list[str], label: str) -> Check:
    """Run pytest with given args and return pass/fail."""
    cmd = [sys.executable, "-m", "pytest"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr
    # Find summary line
    summary = ""
    for line in reversed(output.splitlines()):
        if "passed" in line or "failed" in line or "error" in line:
            summary = line.strip()
            break
    passed = result.returncode == 0
    detail = summary if not passed else summary
    return Check(label, passed, detail)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="FleziBCG backend verification")
    parser.add_argument(
        "--testenv-only",
        action="store_true",
        help="Run only import, DB, and testenv checks (skip full suite)",
    )
    parser.add_argument(
        "--full-suite-twice",
        action="store_true",
        help="Run full backend suite twice for repeat-run stability check",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("FleziBCG Backend Verification (BACKEND-QA-BASELINE-02)")
    print("=" * 60)
    print()
    print("Compose file:  docker/docker-compose.db.yml")
    print("Backend entry: app.main")
    print()

    results: list[Check] = []

    # 1. Import check
    print("[1/5] Backend import check ...")
    results.append(check_backend_import())

    # 2. Ruff lint
    print("[2/5] Ruff lint check ...")
    results.append(check_ruff_lint())

    # 3. DB connectivity
    print("[3/5] DB connectivity check ...")
    db_check = check_db_connectivity()
    results.append(db_check)
    if not db_check.passed:
        _print_results(results)
        print("STOP: DB is not reachable. Fix DB connectivity before running tests.")
        print()
        print(_DEV_DB_START_HINT)
        return 1

    # 4. Focused testenv tests
    print("[4/5] Focused testenv tests ...")
    results.append(
        check_pytest(
            [
                "tests/test_testenv_db_safety.py",
                "tests/test_testenv_db_connectivity_contract.py",
                "-q",
                "--tb=short",
            ],
            "Testenv safety + connectivity contract",
        )
    )

    if args.testenv_only:
        _print_results(results)
        all_passed = all(c.passed for c in results)
        if all_passed:
            print("OK: testenv-only checks passed.")
        else:
            print("FAIL: one or more checks failed.")
        return 0 if all_passed else 1

    # 5. Full backend pytest suite
    runs = 2 if args.full_suite_twice else 1
    for i in range(1, runs + 1):
        label = (
            f"Full backend suite (run {i}/{runs})"
            if runs > 1
            else "Full backend suite"
        )
        print(f"[5/5] {label} ...")
        results.append(check_pytest(["tests/", "-q", "--tb=short"], label))

    _print_results(results)
    all_passed = all(c.passed for c in results)
    if all_passed:
        print("OK: all backend verification checks passed.")
    else:
        print("FAIL: one or more backend verification checks failed.")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

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
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_COMPOSE_FILE = "docker/docker-compose.db.yml"
_COMPOSE_DB_SERVICE = "db"


def _candidate_search_roots(anchors: Iterable[Path]) -> list[Path]:
    roots: list[Path] = []
    seen: set[Path] = set()
    for anchor in anchors:
        resolved = anchor.resolve()
        start = resolved.parent if resolved.suffix else resolved
        for candidate in (start, *start.parents):
            if candidate not in seen:
                seen.add(candidate)
                roots.append(candidate)
    return roots


def _find_backend_root(anchor: Path) -> Path:
    for root in _candidate_search_roots([anchor]):
        if (root / "app" / "__init__.py").is_file() and (root / "scripts").is_dir():
            return root
        backend_root = root / "backend"
        if (backend_root / "app" / "__init__.py").is_file() and (
            backend_root / "scripts"
        ).is_dir():
            return backend_root
    raise RuntimeError(f"Could not locate backend root from anchor: {anchor}")


def _find_repo_file(*relative_parts: str, anchors: Iterable[Path]) -> Path | None:
    for root in _candidate_search_roots(anchors):
        candidate = root.joinpath(*relative_parts)
        if candidate.is_file():
            return candidate
    return None


def _bootstrap_backend_path(backend_root: Path) -> None:
    backend_root_str = str(backend_root)
    if backend_root_str not in sys.path:
        sys.path.insert(0, backend_root_str)


def _run_in_backend_root(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(BACKEND_ROOT),
        capture_output=True,
        text=True,
    )


SCRIPT_PATH = Path(__file__).resolve()
BACKEND_ROOT = _find_backend_root(SCRIPT_PATH)
REPO_ROOT = _find_repo_file(
    ".github",
    "workflows",
    "pr-gate.yml",
    anchors=[Path.cwd(), BACKEND_ROOT, SCRIPT_PATH],
)
REPO_ROOT = REPO_ROOT.parents[2] if REPO_ROOT is not None else None
COMPOSE_FILE_PATH = _find_repo_file(
    "docker",
    "docker-compose.db.yml",
    anchors=[Path.cwd(), BACKEND_ROOT, SCRIPT_PATH],
)
_bootstrap_backend_path(BACKEND_ROOT)

_DEV_DB_START_HINT = (
    "  To start the dev/test DB:\n"
    f"    docker compose -f {COMPOSE_FILE_PATH or _COMPOSE_FILE} up -d {_COMPOSE_DB_SERVICE}\n"
    f"  Compose file: {COMPOSE_FILE_PATH or _COMPOSE_FILE}  (service: {_COMPOSE_DB_SERVICE}, port: 5432)\n"
    "  Backend env:  backend/.env  (POSTGRES_HOST=localhost, POSTGRES_PORT=5432)\n"
    "  If the container exists but port is not bound, use --force-recreate:\n"
    f"    docker compose -f {COMPOSE_FILE_PATH or _COMPOSE_FILE} up -d --force-recreate {_COMPOSE_DB_SERVICE}"
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

        detail = f"{type(exc).__name__}: {exc}\n{_DEV_DB_START_HINT}"
        return Check(
            f"DB connectivity ({_mask_url(raw_url)})",
            False,
            detail,
        )


def check_ruff_lint() -> Check:
    """Run ruff check . and return pass/fail. Requires ruff in PATH or PYTHONPATH."""
    cmd = [sys.executable, "-m", "ruff", "check", "."]
    result = _run_in_backend_root(cmd)
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


def check_ruff_format() -> Check:
    """Run ruff format --check . and return pass/fail (BACKEND-QA-BASELINE-03)."""
    cmd = [sys.executable, "-m", "ruff", "format", "--check", "."]
    result = _run_in_backend_root(cmd)
    output = (result.stdout + result.stderr).strip()
    passed = result.returncode == 0
    if passed:
        return Check("Ruff format (ruff format --check .)", True, "")
    summary = ""
    for line in reversed(output.splitlines()):
        if "would reformat" in line or "reformatted" in line or "unchanged" in line:
            summary = line.strip()
            break
    return Check("Ruff format (ruff format --check .)", False, summary or output[:200])


def check_pytest(args: list[str], label: str) -> Check:
    """Run pytest with given args and return pass/fail."""
    cmd = [sys.executable, "-m", "pytest"] + args
    result = _run_in_backend_root(cmd)
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


def _all_checks_passed(results: list[Check], *, testenv_only: bool) -> bool:
    if not testenv_only:
        return all(check.passed for check in results)
    return all(
        check.passed or check.name == "Ruff format (ruff format --check .)"
        for check in results
    )


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
    print("FleziBCG Backend Verification (BACKEND-QA-BASELINE-03)")
    print("=" * 60)
    print()
    print(f"Backend root: {BACKEND_ROOT}")
    print(f"Repo root:    {REPO_ROOT or '<not-found>'}")
    print(f"Compose file:  {COMPOSE_FILE_PATH or _COMPOSE_FILE}")
    print("Backend entry: app.main")
    print("Canonical invocation (repo root): python backend/scripts/verify_backend.py")
    print("Canonical invocation (backend dir): python scripts/verify_backend.py")
    print()

    results: list[Check] = []

    # 1. Import check
    print("[1/5] Backend import check ...")
    results.append(check_backend_import())

    # 2. Ruff lint
    print("[2/5] Ruff lint check ...")
    results.append(check_ruff_lint())

    # 2b. Ruff format check (BACKEND-QA-BASELINE-03)
    print("[2b/5] Ruff format check ...")
    results.append(check_ruff_format())

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
        all_passed = _all_checks_passed(results, testenv_only=True)
        if all_passed:
            if not results[2].passed:
                print(
                    "NOTE: ruff format --check remains report-only for --testenv-only;"
                    " cleanup is deferred to MECH-FORMAT-01."
                )
            print("OK: testenv-only checks passed.")
        else:
            print("FAIL: one or more checks failed.")
        return 0 if all_passed else 1

    # 5. Full backend pytest suite
    runs = 2 if args.full_suite_twice else 1
    for i in range(1, runs + 1):
        label = (
            f"Full backend suite (run {i}/{runs})" if runs > 1 else "Full backend suite"
        )
        print(f"[5/5] {label} ...")
        results.append(check_pytest(["tests/", "-q", "--tb=short"], label))

    _print_results(results)
    all_passed = _all_checks_passed(results, testenv_only=False)
    if all_passed:
        print("OK: all backend verification checks passed.")
    else:
        print("FAIL: one or more backend verification checks failed.")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

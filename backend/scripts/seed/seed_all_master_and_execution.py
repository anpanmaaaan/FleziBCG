#!/usr/bin/env python3
"""
Complete seed data orchestrator.

Runs all seed scripts in the correct order:
1. Products & Routings (master data)
2. Execution Test Data (operations in stations)
3. Verification

Usage:
  cd backend
    .venv\\Scripts\\python scripts/seed/seed_all_master_and_execution.py
"""

import subprocess
import sys
from pathlib import Path


SEED_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SEED_DIR.parent.parent


def run_seed_script(script_name: str, description: str) -> bool:
    """Run a seed script and report result."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"{'=' * 60}")
    module_name = f"scripts.seed.{Path(script_name).stem}"

    try:
        result = subprocess.run(
            [sys.executable, "-m", module_name],
            cwd=str(BACKEND_DIR),
            check=True,
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FAILED: {description}")
        print(f"Exit code: {e.returncode}")
        return False


def main():
    """Run all seed scripts."""
    print("\n" + "=" * 60)
    print("COMPLETE SEED DATA ORCHESTRATOR")
    print("=" * 60)
    print("\nThis will create:")
    print("  1. Products (6 total)")
    print("  2. Routings (3 total) with Operations")
    print("  3. Resource Requirements")
    print("  4. Production Orders linked to Master Data")
    print("  5. Execution Test Data (Operations & Sessions)")
    print("  6. Users & Roles")

    results = []

    # Step 1: Seed master data
    results.append(
        run_seed_script(
            "seed_products_and_routing.py",
            "STEP 1: Master Data (Products & Routings)",
        )
    )

    # Step 2: Seed production orders with master data
    results.append(
        run_seed_script(
            "seed_production_orders_with_master_data.py",
            "STEP 2: Production Orders (Linked to Master Data)",
        )
    )

    # Step 3: Seed execution data
    results.append(
        run_seed_script(
            "seed_test_data.py",
            "STEP 3: Execution Test Data (Operations & Sessions)",
        )
    )

    # Summary
    print("\n" + "=" * 60)
    if all(results):
        print("✓ ALL SEED OPERATIONS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\n✓ Master Data: 6 products, 3 routings with operations")
        print("✓ Production Orders: 3 POs with 9 operations total")
        print("✓ Execution Data: 3 scenarios with operations and session states")
        print("✓ Multi-station setup: STATION-A through STATION-E")
        print("\nDatabase ready for testing:")
        print("  - Frontend: http://localhost (demo/demo123)")
        print("  - API Docs: http://localhost:8010/docs")
        print("  - Database: psql -h localhost -U mes -d mes -W")
        print()
        return 0
    else:
        print("❌ SOME OPERATIONS FAILED")
        print("=" * 60)
        print("\nCheck output above for details")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())

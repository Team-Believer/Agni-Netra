"""
Agni-Netra: Demonstration Database Seeder
=========================================
Referenced in README.md quickstart step:
    python scripts/seed_demo_data.py
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tests.fixtures.seed_test_data import seed_test_database

if __name__ == "__main__":
    print("==========================================================")
    print("  Agni-Netra: Seeding Realistic Spaceborne Demo Data")
    print("==========================================================")
    seed_test_database()
    print("\n[OK] Seeding complete! Database is ready for dashboard & live map.")

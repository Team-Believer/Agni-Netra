"""
Agni-Netra: Demonstration Database Seeder
=========================================
Seeds the local SQLite database with realistic spaceborne thermal anomaly events,
multi-sensor evidence chains (VIIRS 375m, INSAT-3DS Rapid Imager, Sentinel-2 MSI,
Sentinel-1 SAR, IMD Weather, OSM Critical Infrastructure), risk indices, priority
scores, and operational alerts across India.

Usage:
    python scripts/seed_demo.py
    python scripts/seed_demo_data.py
    python seed_demo.py
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tests.fixtures.seed_test_data import seed_test_database

def main():
    print("==========================================================")
    print("  Agni-Netra: Seeding Realistic Spaceborne Demo Data")
    print("==========================================================")
    seed_test_database()
    print("\n[OK] Seeding complete! Database is ready for dashboard & live map.")

if __name__ == "__main__":
    main()

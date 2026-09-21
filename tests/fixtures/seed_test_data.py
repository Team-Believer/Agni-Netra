import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.seed import seed_database

def seed_test_database():
    """
    Delegate test database seeding to the central master seed database implementation.
    This guarantees 100% data consistency across test fixtures, demo scripts, and main backend.
    """
    seed_database()

if __name__ == "__main__":
    seed_test_database()

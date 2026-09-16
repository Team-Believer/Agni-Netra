import sys
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.database.database import init_db, SessionLocal
from backend.app.pipeline.ingestion_pipeline import IngestionPipeline

def main():
    print("Initializing Agni-Netra database & tables...")
    init_db()
    db = SessionLocal()
    try:
        pipeline = IngestionPipeline(db)
        result = pipeline.run_cycle()
        print("\n=== Pipeline Execution Summary ===")
        print(json.dumps(result, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    main()

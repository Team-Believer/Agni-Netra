import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.core.config import settings
from backend.app.core.logging import logger

# Ensure parent directory of database exists
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///"):
    db_path = db_url.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes the database tables."""
    from backend.app.database import models # noqa: F401
    logger.info("Initializing SQLite database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

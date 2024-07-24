import os
from sqlalchemy import create_engine, __version__ as sqlalchemy_version
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql
import traceback

from utils.logger import setup_logging
logger = setup_logging()

# Determine the environment
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")

# Set up environment-specific database URLs
DATABASE_URLS = {
    "local": "postgresql://betterfantasy:betterfantasy@localhost:5432/better_fantasy",
    "dev": os.environ.get("DEV_POSTGRES_URL"), 
    "prod": os.environ.get("PROD_POSTGRES_URL")
}

# Select the appropriate database URL
DATABASE_URL = DATABASE_URLS.get(ENVIRONMENT)

if not DATABASE_URL:
    raise ValueError(f"Database URL not set for environment: {ENVIRONMENT}")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Debug print
print(f"Using DATABASE_URL: {DATABASE_URL}")
logger.info(f"Database URL: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print(f"Connected to database for environment: {ENVIRONMENT}")
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Determine the environment
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")

# Set up environment-specific database URLs
DATABASE_URLS = {
    "local": "postgresql://betterfantasy:betterfantasy@localhost:5432/better_fantasy",
    "dev": os.environ.get("POSTGRES_URL"), 
    "prod": os.environ.get("PROD_POSTGRES_URL")
}

# Select the appropriate database URL
DATABASE_URL = DATABASE_URLS.get(ENVIRONMENT)

if not DATABASE_URL:
    raise ValueError(f"Database URL not set for environment: {ENVIRONMENT}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print(f"Connected to database for environment: {ENVIRONMENT}")
import os
from sqlalchemy import create_engine, __version__ as sqlalchemy_version
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql

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

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    connect_args={
        "ssl": {
            "ssl_mode": "require",  # Changed from "verify-full" to "require"
            # Removed "sslrootcert" as it's not typically needed for Vercel deployments
        }
    } if ENVIRONMENT != "local" else {}  # Only use SSL for non-local environments
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

# Additional debug information
import sys
print(f"Python version: {sys.version}")
print(f"SQLAlchemy version: {sqlalchemy.__version__}")
try:
    import psycopg2
    print(f"psycopg2 version: {psycopg2.__version__}")
    print(f"psycopg2 path: {psycopg2.__file__}")
except ImportError:
    print("psycopg2 is not installed")
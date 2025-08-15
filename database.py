from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# MySQL connection - replace with your actual credentials
DB_HOST = "magicfingers.com.pk"  # Production host
DB_USER = "magicfin_industries"
DB_PASSWORD = "magicfin_industries"
DB_NAME = "magicfin_industries"

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Configure engine with connection pool and timeout settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Validates connections before use
    pool_recycle=3600,   # Recycle connections every hour
    pool_timeout=30,     # Timeout when getting connection from pool
    max_overflow=20,     # Allow up to 20 connections beyond pool_size
    echo=False           # Set to True for debugging SQL queries
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session with retry logic"""
    db = SessionLocal()
    try:
        # Test the connection to ensure it's alive
        db.execute("SELECT 1")
        yield db
    except Exception as e:
        # If connection fails, try to recreate it
        db.close()
        db = SessionLocal()
        yield db
    finally:
        db.close()
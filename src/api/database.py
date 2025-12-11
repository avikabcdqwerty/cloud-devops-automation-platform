import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.url import URL

from src.api.models import Base

# Configure logging for database operations
logger = logging.getLogger("cloud-devops-api.database")

# Database connection settings (use environment variables for security)
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "cloud_devops_db")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create SQLAlchemy engine
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,  # Set to True for SQL debug logs
        future=True
    )
    logger.info("Database engine created successfully.")
except SQLAlchemyError as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

def init_db() -> None:
    """
    Initialize the database by creating all tables.
    Should be called at application startup or migration.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created or verified successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {e}")
        raise

# Exported: engine, SessionLocal, init_db
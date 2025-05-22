"""
PostgreSQL database setup using SQLAlchemy.

Provides engine, session, and base for ORM models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import get_env_variable

# Get DB URL from environment
DATABASE_URL = get_env_variable(
    "POSTGRES_URL",
    "postgresql://postgres:postgres@localhost:5432/ai_microservices?client_encoding=utf8"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"client_encoding": "utf8"}
)
# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

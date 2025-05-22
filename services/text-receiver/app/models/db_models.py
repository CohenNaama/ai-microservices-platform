"""
SQLAlchemy ORM models for PostgreSQL.

Defines the structure of the 'processed_texts' table.
"""

from sqlalchemy import Column, Integer, DateTime, Unicode
from core.db import Base
from datetime import datetime


class ProcessedText(Base):
    """
    ORM model for processed text storage.
    """
    __tablename__ = "processed_texts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Unicode, nullable=False)
    original_text = Column(Unicode, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

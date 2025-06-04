"""
Utility script to create all PostgreSQL tables using SQLAlchemy ORM.
"""

from app.core.db import Base, engine
from models.db_models import ProcessedText

# Create tables
Base.metadata.create_all(bind=engine)
print("✅ Tables created.")

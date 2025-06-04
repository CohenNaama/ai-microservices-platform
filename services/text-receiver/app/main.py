"""
Entry point for the FastAPI application.

Initializes the app, registers routers and global exception handlers.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from app.api.routes import router
from app.core.exception_handlers import validation_exception_handler, global_exception_handler
from app.core.kafka_consumer import _consume_loop
from app.core.db import engine
from app.models.db_models import Base
from app.core.logging_config import logger
import threading


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application lifespan events.

    - Creates DB tables if not already existing
    - Starts Kafka consumer in a background thread
    """
    logger.info("Starting lifespan")

    # Ensure DB schema is ready
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.exception("Failed to create database tables: %s", e)

    # Start Kafka consumer
    thread = threading.Thread(target=_consume_loop, daemon=True)
    thread.start()
    logger.info("Kafka consumer thread started.")

    yield

    logger.info("Shutting down lifespan")


app = FastAPI(
    title="Text Receiver Service",
    description="Receives text input and publishes it to Kafka.",
    version="1.0.0",
    lifespan=lifespan
)

# Register routes and exception handlers
app.include_router(router)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

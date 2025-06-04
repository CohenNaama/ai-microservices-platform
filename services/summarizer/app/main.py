"""
FastAPI app entry point for the Summarizer microservice.

Initializes the application, registers routers and handlers,
and launches the Kafka consumer in the background.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from app.core.kafka_consumer import _consume_loop
from app.core.logging_config import logger
from app.api.routes import router
from app.core.init_db import init_db
from app.core.exception_handlers import validation_exception_handler, global_exception_handler
import threading


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown lifecycle.

    Starts the Kafka consumer loop in a background thread.
    """
    logger.info("Starting Summarizer lifespan...")

    try:
        # Initialize database tables
        init_db()
        logger.info("Database tables created (if not exist).")

        # Start Kafka consumer
        thread = threading.Thread(target=_consume_loop, daemon=True)
        thread.start()
        logger.info("Kafka consumer thread started.")
    except Exception as e:
        logger.exception("Failed during startup: %s", e)

    yield

    logger.info("Shutting down Summarizer lifespan.")


app = FastAPI(
    title="Summarizer Microservice",
    description="Consumes text from Kafka and summarizes it using OpenAI.",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(router)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

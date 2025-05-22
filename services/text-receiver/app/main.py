"""
Entry point for the FastAPI application.

Initializes the app, registers routers and global exception handlers.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from api.routes import router
from core.exception_handlers import validation_exception_handler, global_exception_handler
from core.kafka_consumer import _consume_loop
from core.logging_config import logger


import threading


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application lifespan events.

    Starts Kafka consumer in a background thread on startup.
    """
    logger.info("🔄 Starting lifespan")

    thread = threading.Thread(target=_consume_loop, daemon=True)
    thread.start()

    logger.info("✅ Yielding lifespan")
    yield

    logger.info("🛑 Shutting down lifespan")


app = FastAPI(
    title="Text Receiver Service",
    description="Receives text input and publishes it to Kafka.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

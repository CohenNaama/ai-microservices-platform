"""
Entry point for the FastAPI application.

Initializes the app, registers routers and global exception handlers.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.api.routes import router
from app.core.exception_handlers import validation_exception_handler, global_exception_handler


app = FastAPI(
    title="Text Receiver Service",
    description="Receives text input and publishes it to Kafka.",
    version="1.0.0"
)

app.include_router(router)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

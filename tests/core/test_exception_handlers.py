"""
Tests for custom exception handlers (422 & 500) in FastAPI.

Validates that validation errors and unexpected exceptions are correctly handled by global handlers.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Body
from fastapi.exceptions import RequestValidationError
from app.core.exception_handlers import validation_exception_handler, global_exception_handler

app = FastAPI()

# Register the custom handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


@app.post("/test/422")
async def trigger_422_endpoint(text: str = Body(...)):
    """
    Simulates a request with expected validation error if 'text' is missing.
    """
    return {"text": text}


@app.get("/test/500")
async def trigger_500_endpoint():
    """
    Simulates an unhandled exception to test 500 handler.
    """
    raise RuntimeError("Unexpected crash")


client = TestClient(app, raise_server_exceptions=False)


@pytest.mark.api
def test_validation_error_422_custom_handler():
    """
    Test that missing required field triggers 422 handler.

    Verifies custom response format and content.
    """
    response = client.post("/test/422", json={})
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.api
def test_global_exception_500_handler():
    """
    Test that unexpected error triggers global exception handler (500).

    Validates generic response and status code.
    """
    response = client.get("/test/500")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}

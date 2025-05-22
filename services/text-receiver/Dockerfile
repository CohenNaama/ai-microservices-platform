# Base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Set environment for UTF-8 support
ENV PYTHONPATH=/app
ENV PYTHONIOENCODING=UTF-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install locales and dependencies
COPY app/ /app/
COPY requirements.txt .

RUN apt-get update && apt-get install -y locales \
    && echo "C.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--lifespan", "on"]

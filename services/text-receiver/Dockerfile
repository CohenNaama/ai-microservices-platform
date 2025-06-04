# Base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /usr/src/app
ENV PYTHONPATH=/usr/src/app

# Set UTF-8 environment variables
ENV PYTHONIOENCODING=UTF-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Copy app source code and requirements
COPY app /usr/src/app/app
COPY requirements.txt .

# Install dependencies
RUN apt-get update && apt-get install -y locales \
    && echo "C.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--lifespan", "on"]

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY pubmedllm/ /app/pubmedllm/

# Set Python path
ENV PYTHONPATH=/app

# Start an interactive shell instead of running main.py
CMD ["bash"]
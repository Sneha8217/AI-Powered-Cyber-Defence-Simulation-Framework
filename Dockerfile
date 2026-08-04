# Use official python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for compiling numerical modules
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source tree
COPY . .

# Expose API dashboard and services ports
EXPOSE 8030 8010 8020

# Run entry point integration script
CMD ["python", "member4/main.py"]

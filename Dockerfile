# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies if required (none currently explicitly needed for requests/fastapi)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set PYTHONPATH to the current directory (project root)
# This ensures that 'server.movie_service' can be imported by cli.py
ENV PYTHONPATH=/app

# Define the entrypoint to run the CLI
ENTRYPOINT ["python", "cli.py"]

# Default command (can be overridden during docker run)
CMD ["--mock"]

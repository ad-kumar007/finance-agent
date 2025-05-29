# Start from the base Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# System dependencies for whisper, ffmpeg, etc.
RUN apt-get update && \
    apt-get install -y ffmpeg build-essential libssl-dev libffi-dev git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Clean pip cache & install Python dependencies safely
RUN pip install --upgrade pip && \
    pip cache purge && \
    pip install --no-cache-dir --no-deps -r requirements.txt

# Copy your app code
COPY . .

# Set entrypoint or default CMD
# Base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy wheelhouse and requirements
COPY wheelhouse /wheelhouse
COPY requirements.txt .

# Install dependencies from wheelhouse
RUN pip install --find-links=/wheelhouse -r requirements.txt

# Copy the entire codebase
COPY . .

# Run FastAPI app with uvicorn
CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8001"]


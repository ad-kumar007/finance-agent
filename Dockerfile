# Use full Python base image (not slim) to avoid missing dependencies
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy only requirements first (use cache)
COPY requirements.txt .

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python packages
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all code after installing dependencies
COPY . .

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]

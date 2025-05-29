# Base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies from PyPI
RUN pip install -r requirements.txt

# Copy the entire codebase
COPY . .

# Run your app (update path if needed)
CMD ["python", "orchestrator/main.py"]

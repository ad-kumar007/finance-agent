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

# Run your app (update the path to main.py)
CMD ["python", "orchestrator/main.py"]

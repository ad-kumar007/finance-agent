# Use slim Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy only requirements first for layer caching
COPY requirements.txt .

# Install ffmpeg (for audio processing)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# ✅ Make the launch script executable using the correct path
RUN chmod +x orchestrator/launch.sh

# Expose FastAPI and Streamlit ports
EXPOSE 8000 8501

# ✅ Run the launch script using the correct path
CMD ["sh", "orchestrator/launch.sh"]

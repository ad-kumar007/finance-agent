#!/bin/bash
# Build script for Render

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p audio
mkdir -p faiss_index

echo "Build complete!"

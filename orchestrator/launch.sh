#!/bin/bash

# Start FastAPI server
uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit app
streamlit run streamlit_app/app.py --server.port 8501

#!/bin/bash

uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000 &

streamlit run streamlit_app.py --server.port 8501

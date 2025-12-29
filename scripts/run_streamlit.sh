#!/bin/bash
# Script to run Streamlit UI

cd "$(dirname "$0")/.."

echo "Starting Jobly Streamlit UI..."

cd backend
poetry run streamlit run jobly/ui/streamlit/app.py --server.port=8501

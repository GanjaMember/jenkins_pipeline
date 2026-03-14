#!/bin/bash
# Stage 1: Download data

# Activate virtual environment or create if missing
if [ ! -d "./my_env" ]; then
    python3 -m venv ./my_env
fi
. ./my_env/bin/activate

# Ensure pip and setuptools are up-to-date
python3 -m ensurepip --upgrade
pip install --upgrade pip setuptools

# Install requirements
pip install -r requirements.txt

# Run download script
python3 scripts/python/download.py
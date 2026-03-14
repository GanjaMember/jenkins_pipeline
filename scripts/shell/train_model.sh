#!/bin/bash
# Stage 2: Train model

# Activate virtual environment
. ./my_env/bin/activate

# Run training script, save best model path
python3 scripts/python/train_model.py
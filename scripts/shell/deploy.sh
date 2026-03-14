#!/bin/bash
# Stage 3: Deploy ML model as MLflow service

. ./my_env/bin/activate

# Prevent Jenkins from killing the background MLflow processes
export BUILD_ID=dontKillMe
export JENKINS_NODE_COOKIE=dontKillMe

# Read path of trained model
path_model=$(cat best_model.txt)

echo "Best model path from train stage:"
cat best_model.txt

# Start MLflow service in background on port 5003
mlflow models serve -m "$path_model" -p 5003 --no-conda &
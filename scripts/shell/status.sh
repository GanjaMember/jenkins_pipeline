#!/bin/bash
# Stage 4: Check model service status via curl

MLFLOW_URL="http://127.0.0.1:5003/invocations"
INPUT_FILE="./data/my_input.json"

# Wait until MLflow is ready (up to 30 seconds)
echo "Waiting for MLflow to start..."
for i in {1..30}; do
    if curl -s "$MLFLOW_URL" -H "Content-Type:application/json" --data @"$INPUT_FILE" >/dev/null 2>&1; then
        echo "MLflow is ready!"
        break
    fi
    sleep 1
done

# Send the actual request and capture response
echo "Sending test input to MLflow model..."
response=$(curl -s "$MLFLOW_URL" -H "Content-Type:application/json" --data @"$INPUT_FILE")

echo "Prediction response from MLflow:"
echo "$response"
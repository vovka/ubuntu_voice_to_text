#!/bin/bash

# Activate virtual environment
source /app/venv/bin/activate

# Check if we are in test mode
if [ "$1" = "test" ]; then
    echo "🧪 Running tests..."
    shift  # Remove "test" from arguments
    exec pytest tests/ --cov=. --cov-report=term-missing -v "$@"
elif [ "$1" = "lint" ]; then
    echo "🔍 Running linting..."
    echo "Running flake8..."
    flake8 . --max-line-length=88
    echo "Checking code formatting with black..."
    black --check --diff .
    echo "✅ All linting checks passed!"
elif [ "$1" = "format" ]; then
    echo "🎨 Formatting code with black..."
    black .
    echo "✅ Code formatted!"
elif [ "$1" = "shell" ]; then
    echo "🐚 Starting interactive shell..."
    exec /bin/bash
else
    # Check if Vosk model is available
    MODEL_PATH="/opt/vosk-model-small-en-us-0.15"
    if [ ! -d "$MODEL_PATH" ] || [ ! "$(ls -A $MODEL_PATH)" ]; then
        echo "❌ Vosk model not found at $MODEL_PATH"
        echo "Please ensure the model is mounted or downloaded:"
        echo "  1. Run ./download-model.sh to download the model locally"
        echo "  2. Mount it with: -v ./vosk-model:/opt/vosk-model-small-en-us-0.15:ro"
        echo ""
        echo "For CI/CD environments, ensure the model is downloaded in a setup step:"
        echo "  mkdir -p vosk-model"
        echo "  wget -O model.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        echo "  unzip model.zip && mv vosk-model-small-en-us-0.15/* vosk-model/"
        exit 1
    fi

    echo "✅ Vosk model found at $MODEL_PATH"

    # Run the application
    python3 /app/voice_typing.py
fi
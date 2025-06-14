#!/bin/bash

# Script to download Vosk model for the Ubuntu Voice to Text application
# NOTE: This script is now optional. The Vosk model is included in the Docker image.
# This script can be used for manual installations or if you want to pre-download 
# the model to speed up Docker builds in environments with slow network connections.

MODEL_DIR="vosk-model-small-en-us-0.15"
MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_ZIP="vosk-model-small-en-us-0.15.zip"

echo "Downloading Vosk model for Ubuntu Voice to Text..."
echo "NOTE: This is optional when using Docker, as the model is automatically downloaded."

# Create model directory if it doesn't exist
mkdir -p "$MODEL_DIR"

# Download model if directory is empty
if [ ! "$(ls -A $MODEL_DIR 2>/dev/null)" ]; then
    echo "Downloading model from $MODEL_URL..."
    wget -O "$MODEL_ZIP" "$MODEL_URL"
    
    echo "Extracting model..."
    unzip "$MODEL_ZIP" -d "$MODEL_DIR"
    
    # Clean up
    rm -f "$MODEL_ZIP"
    
    echo "Model downloaded and extracted to $MODEL_DIR/"
else
    echo "Model already exists in $MODEL_DIR/"
fi

echo "Model setup complete!"
echo ""
echo "For manual installation, set the model path:"
echo "  export VOSK_MODEL_PATH=\"$(pwd)/$MODEL_DIR\""
echo "  python main.py"
echo ""
echo "For Docker usage:"
echo "  docker-compose up --build"
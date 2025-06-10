#!/bin/bash

# Script to download Vosk model for the Ubuntu Voice to Text application

MODEL_DIR="vosk-model"
MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_ZIP="vosk-model-small-en-us-0.15.zip"

echo "Downloading Vosk model for Ubuntu Voice to Text..."

# Create model directory if it doesn't exist
mkdir -p "$MODEL_DIR"

# Download model if directory is empty
if [ ! "$(ls -A $MODEL_DIR)" ]; then
    echo "Downloading model from $MODEL_URL..."
    wget -O "$MODEL_ZIP" "$MODEL_URL"
    
    echo "Extracting model..."
    unzip "$MODEL_ZIP" -d temp_extract
    
    # Move contents to the model directory
    mv temp_extract/vosk-model-small-en-us-0.15/* "$MODEL_DIR/"
    
    # Clean up
    rm -rf temp_extract "$MODEL_ZIP"
    
    echo "Model downloaded and extracted to $MODEL_DIR/"
else
    echo "Model already exists in $MODEL_DIR/"
fi

echo "Model setup complete!"
echo "You can now run: docker-compose up --build"
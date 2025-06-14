#!/bin/bash
set -euo pipefail

# Poetry doesn't need venv activation in Docker since we disabled virtualenvs.create

# Fix permissions for /models if running as root and UID/GID are set
if [ "$(id -u)" = "0" ] && [ -n "${UID:-}" ] && [ -n "${GID:-}" ]; then
    echo "Fixing ownership of /models to $UID:$GID ..."
    chown -R "$UID:$GID" /models 2>/dev/null || true
fi

# Check if we are in test mode
if [ "${1:-}" = "test" ]; then
    echo "🧪 Running tests..."
    shift  # Remove "test" from arguments
    exec poetry run pytest tests/ --cov=. --cov-report=term-missing -v "$@"
elif [ "${1:-}" = "lint" ]; then
    echo "🔍 Running linting..."
    echo "Running flake8..."
    poetry run flake8 . --max-line-length=88
    echo "Checking code formatting with black..."
    poetry run black --check --diff .
    echo "✅ All linting checks passed!"
elif [ "${1:-}" = "format" ]; then
    echo "🎨 Formatting code with black..."
    poetry run black .
    echo "✅ Code formatted!"
elif [ "${1:-}" = "shell" ]; then
    echo "🐚 Starting interactive shell..."
    exec /bin/bash
else
    # Vosk model management
    MODEL_DIR="/models/vosk-model-small-en-us-0.15"
    MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    ZIP_PATH="/models/model.zip"

    # Create models directory if it doesn't exist
    mkdir -p /models

    # Check if Vosk model exists and is complete
    if [ ! -d "$MODEL_DIR" ] || [ ! "$(ls -A "$MODEL_DIR" 2>/dev/null)" ] || [ ! -f "$MODEL_DIR/conf/model.conf" ]; then
        echo "🔄 Vosk model not found or incomplete, downloading..."
        echo "📥 Downloading from: $MODEL_URL"

        # Clean up any partial downloads
        rm -rf "$MODEL_DIR" "$ZIP_PATH"

        # Download with retry logic
        MAX_ATTEMPTS=3
        ATTEMPT=1

        while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
            echo "📥 Download attempt $ATTEMPT/$MAX_ATTEMPTS..."

            # Download the model
            if wget --timeout=30 --tries=1 -O "$ZIP_PATH" "$MODEL_URL"; then
                echo "✅ Model downloaded successfully"

                # Extract the model
                echo "📦 Extracting model..."
                if unzip -q "$ZIP_PATH" -d /models; then
                    echo "✅ Model extracted successfully"

                    # Verify extraction was successful
                    if [ -d "$MODEL_DIR" ] && [ -f "$MODEL_DIR/conf/model.conf" ]; then
                        echo "✅ Model verification successful"
                        rm -f "$ZIP_PATH"
                        break
                    else
                        echo "❌ Model verification failed - extracted files incomplete"
                        rm -rf "$MODEL_DIR" "$ZIP_PATH"
                    fi
                else
                    echo "❌ Failed to extract model"
                    rm -f "$ZIP_PATH"
                fi
            else
                echo "❌ Failed to download model (attempt $ATTEMPT/$MAX_ATTEMPTS)"
            fi

            ATTEMPT=$((ATTEMPT + 1))
            if [ $ATTEMPT -le $MAX_ATTEMPTS ]; then
                echo "⏳ Waiting 5 seconds before retry..."
                sleep 5
            fi
        done

        # Final check
        if [ ! -d "$MODEL_DIR" ] || [ ! -f "$MODEL_DIR/conf/model.conf" ]; then
            echo "❌ Failed to download Vosk model after $MAX_ATTEMPTS attempts"
            echo ""
            echo "💡 Troubleshooting:"
            echo "  1. Check your internet connection"
            echo "  2. Verify the model URL is accessible: $MODEL_URL"
            echo "  3. Ensure the /models directory is writable"
            echo "  4. For offline environments, pre-download the model:"
            echo "     mkdir -p ./vosk-models"
            echo "     wget -O model.zip $MODEL_URL"
            echo "     unzip model.zip -d ./vosk-models"
            echo "     # Then mount: -v ./vosk-models:/models:rw"
            exit 1
        fi
    else
        echo "✅ Vosk model found at $MODEL_DIR"
    fi

    # Run the application
    export PYTHONPATH=/app
    exec python3 /app/main.py "$@"
fi

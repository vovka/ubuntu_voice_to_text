FROM python:3.11-slim

# # Update Alpine repositories to fix network issues
# RUN sed -i 's|https://dl-cdn.alpinelinux.org|http://mirror1.hs-esslingen.de/pub/Mirrors/alpine|' /etc/apk/repositories || true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    xdotool \
    pulseaudio \
    alsa-utils \
    portaudio19-dev \
    wget \
    curl \
    unzip \
    python3-pil \
    gcc \
    build-essential \
    linux-headers-amd64 \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Download and install Vosk model directly into the image
RUN mkdir -p /opt/vosk-model-small-en-us-0.15

# Copy application files first
COPY voice_typing.py .
COPY voice_typing.sh .
COPY requirements.txt .
COPY pyproject.toml .
COPY tests/ tests/
COPY docker-entrypoint.sh .

# Make shell script and entrypoint executable
RUN chmod +x voice_typing.sh docker-entrypoint.sh

# Try to copy local model directory if it exists, otherwise try to download
RUN if [ -d "/app/vosk-model" ] && [ "$(ls -A /app/vosk-model 2>/dev/null)" ]; then \
        echo "Using locally available model" && \
        cp -r /app/vosk-model/* /opt/vosk-model-small-en-us-0.15/; \
    else \
        echo "Model not found locally, attempting to download..." && \
        # Try downloading with multiple methods
        (wget --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 -t 2 \
             -O /tmp/vosk-model-small-en-us-0.15.zip \
             https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip && \
         unzip /tmp/vosk-model-small-en-us-0.15.zip -d /tmp && \
         mv /tmp/vosk-model-small-en-us-0.15/* /opt/vosk-model-small-en-us-0.15/ && \
         rm -rf /tmp/vosk-model-small-en-us-0.15.zip /tmp/vosk-model-small-en-us-0.15) || \
        # If download fails, create a placeholder directory structure and a README
        (mkdir -p /opt/vosk-model-small-en-us-0.15/am && \
         echo "# Vosk Model Download Failed" > /opt/vosk-model-small-en-us-0.15/README.md && \
         echo "The Vosk model could not be downloaded during build." >> /opt/vosk-model-small-en-us-0.15/README.md && \
         echo "Please run the download script manually or ensure network access." >> /opt/vosk-model-small-en-us-0.15/README.md && \
         echo "Download the model from: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip" >> /opt/vosk-model-small-en-us-0.15/README.md); \
    fi

# Create virtual environment and install Python dependencies at build time
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org && \
    /app/venv/bin/pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
        sounddevice vosk pyaudio keyboard pynput pystray pillow && \
    /app/venv/bin/pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
        pytest pytest-cov coverage flake8 black

# Set environment variables for audio and display
ENV PULSE_RUNTIME_PATH=/run/user/1000/pulse
ENV XDG_RUNTIME_DIR=/run/user/1000
ENV DISPLAY=:0

# Expose any necessary ports (none needed for this app)

# Set the entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

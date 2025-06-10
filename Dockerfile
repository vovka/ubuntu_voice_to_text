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
    unzip \
    python3-pil \
    gcc \
    build-essential \
    linux-headers-amd64 \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy application files
COPY voice_typing.py .
COPY voice_typing.sh .
COPY requirements.txt .
COPY pyproject.toml .
COPY tests/ tests/
COPY docker-entrypoint.sh .

# Make shell script and entrypoint executable
RUN chmod +x voice_typing.sh docker-entrypoint.sh

# Create directory for Vosk model (to be mounted at runtime)
RUN mkdir -p /opt/vosk-model-small-en-us-0.15

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

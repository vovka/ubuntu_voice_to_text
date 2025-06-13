FROM python:3.11-slim

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

# Copy application files first
COPY main.py .
COPY requirements.txt .
COPY pyproject.toml .
COPY tests/ tests/
COPY voice_typing/ voice_typing/
COPY docker-entrypoint.sh .

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Create virtual environment and install Python dependencies at build time
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org && \
    /app/venv/bin/pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Set environment variables for audio and display
ENV PULSE_RUNTIME_PATH=/run/user/1000/pulse
ENV XDG_RUNTIME_DIR=/run/user/1000
ENV DISPLAY=:0

# Expose any necessary ports (none needed for this app)

# Set the entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

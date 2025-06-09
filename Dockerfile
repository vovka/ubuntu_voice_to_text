FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    xdotool \
    pulseaudio \
    alsa-utils \
    portaudio19-dev \
    python3-dev \
    build-essential \
    wget \
    unzip \
    python3-pil \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy application files
COPY voice_typing.py .
COPY voice_typing.sh .
COPY requirements.txt .

# Make shell script executable
RUN chmod +x voice_typing.sh

# Create directory for Vosk model (to be mounted at runtime)
RUN mkdir -p /opt/vosk-model-small-en-us-0.15

# Create virtual environment and install Python dependencies
# Note: Some packages may require manual installation due to network restrictions
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org || true

# Set environment variables for audio and display
ENV PULSE_RUNTIME_PATH=/run/user/1000/pulse
ENV XDG_RUNTIME_DIR=/run/user/1000
ENV DISPLAY=:0

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Activate virtual environment\n\
source /app/venv/bin/activate\n\
\n\
# Install Python dependencies at runtime\n\
echo "Installing Python dependencies..."\n\
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org sounddevice vosk pyaudio keyboard pynput pystray pillow || echo "Warning: Some packages failed to install"\n\
\n\
# Run the application\n\
python3 /app/voice_typing.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose any necessary ports (none needed for this app)

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
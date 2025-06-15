FROM python:3.12-slim

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
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Install Poetry
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org poetry

# Copy Poetry configuration files first for better layer caching
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not create virtual environment (we'll use the system Python)
RUN poetry config virtualenvs.create false

ARG INSTALL_DEV_DEPS=false
# Install dependencies with increased timeout for network issues
ENV POETRY_REQUESTS_TIMEOUT=60
# Use the build arg to decide which dependencies to install
RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
      poetry install --with=dev --no-root -v ; \
    else \
      poetry install --only=main --no-root -v ; \
    fi
# RUN poetry install --only=main --no-root -v

# Copy application files
COPY main.py .
COPY tests/ tests/
COPY voice_typing/ voice_typing/
COPY scripts/ scripts/

# Make entrypoint executable
RUN chmod +x scripts/docker-entrypoint.sh

# Install the package in development mode
# RUN poetry install --no-root

# Set environment variables for audio and display
# # Commented out as they are set in compose file
# ENV PULSE_RUNTIME_PATH=/run/user/1000/pulse
# ENV XDG_RUNTIME_DIR=/run/user/1000
# ENV DISPLAY=:0

# Expose any necessary ports (none needed for this app)

# Set the entrypoint
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]

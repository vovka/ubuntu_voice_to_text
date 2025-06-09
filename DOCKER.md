# Ubuntu Voice to Text - Docker Setup

This document provides instructions for running the Ubuntu Voice to Text application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)
- A working audio input device (microphone)
- X11 server running (for GUI components)
- Internet connection (for downloading Python dependencies and Vosk model)

## Quick Start with Docker Compose

1. **Clone the repository and navigate to the directory:**
   ```bash
   git clone https://github.com/vovka/ubuntu_voice_to_text.git
   cd ubuntu_voice_to_text
   ```

2. **Download the Vosk speech recognition model:**
   ```bash
   ./download-model.sh
   ```

3. **Build and run the application:**
   ```bash
   # Default (Alpine-based, smaller image):
   docker-compose up --build
   
   # Alternative (Ubuntu-based):
   docker-compose --profile ubuntu up --build voice-typing-ubuntu
   ```

4. **Use the application:**
   - The application will start with a system tray icon
   - Hold `Ctrl+Shift` to activate voice recording
   - Speak while holding the keys
   - Release to process and type the recognized text

## Docker Image Options

This project provides two Docker image variants:

### Alpine-based (Default)
- **Dockerfile**: `Dockerfile` (default)
- **Image size**: ~150MB
- **Use case**: Production deployments where size matters
- **Build**: `docker-compose up --build`

### Ubuntu-based
- **Dockerfile**: `Dockerfile.ubuntu`
- **Image size**: ~350MB
- **Use case**: Development or when compatibility is preferred
- **Build**: `docker-compose --profile ubuntu up --build voice-typing-ubuntu`

## CI/CD Integration

For automated testing and deployment, ensure the Vosk model is available:

### GitHub Actions / CI Pipeline Setup
```yaml
- name: Download Vosk Model
  run: |
    mkdir -p vosk-model
    wget -O model.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip model.zip
    mv vosk-model-small-en-us-0.15/* vosk-model/
    rm -rf vosk-model-small-en-us-0.15 model.zip

- name: Build and Test Docker Image
  run: |
    docker-compose build
    # Add your test commands here
```

### Manual CI Setup
```bash
# Ensure Vosk model is available
MODEL_DIR="vosk-model"
mkdir -p $MODEL_DIR
if [ ! "$(ls -A $MODEL_DIR)" ]; then
    wget -O model.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip model.zip && mv vosk-model-small-en-us-0.15/* vosk-model/
    rm -rf vosk-model-small-en-us-0.15 model.zip
fi

# Build and run
docker-compose up --build
```

## Manual Docker Commands

### Building the Image

```bash
# Alpine version (default)
docker build -t ubuntu-voice-to-text .

# Ubuntu version
docker build -f Dockerfile.ubuntu -t ubuntu-voice-to-text-ubuntu .
```

### Running the Container

```bash
docker run -it --rm \
  --name ubuntu-voice-to-text \
  --network host \
  --privileged \
  -e DISPLAY=$DISPLAY \
  -e PULSE_RUNTIME_PATH=/run/user/1000/pulse \
  -e XDG_RUNTIME_DIR=/run/user/1000 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v /run/user/1000/pulse:/run/user/1000/pulse:rw \
  -v /dev/snd:/dev/snd:rw \
  -v $(pwd)/vosk-model:/opt/vosk-model-small-en-us-0.15:ro \
  --device /dev/snd:/dev/snd \
  ubuntu-voice-to-text
```

## Configuration

### Audio Setup

The container requires access to audio devices. This is achieved through:
- Volume mounting `/dev/snd` for direct audio device access
- PulseAudio socket sharing via `/run/user/1000/pulse`
- Privileged mode for hardware access

### Display Setup

For the system tray icon to work:
- X11 socket is shared via `/tmp/.X11-unix`
- `DISPLAY` environment variable is passed to the container
- Host networking mode is used for seamless X11 communication

### Vosk Model

The Vosk speech recognition model needs to be downloaded separately:
1. Run `./download-model.sh` to download the model
2. The model is mounted as a volume in the container
3. Alternative: manually download from https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

**Important**: The application will check for the model at startup and provide clear error messages if missing.

### Permissions

The container runs in privileged mode to access audio hardware. For enhanced security in production:
1. Use specific device permissions instead of privileged mode
2. Create a dedicated user with audio group membership
3. Use security contexts to limit capabilities

## Troubleshooting

### Model Not Found Error
```
❌ Vosk model not found at /opt/vosk-model-small-en-us-0.15
```
**Solution**: 
1. Run `./download-model.sh` before starting the container
2. Ensure the `vosk-model` directory contains the extracted model files
3. For CI/CD: Download model in setup step as shown above

### Python Dependencies Installation Issues
Dependencies are now installed at build time for better reliability.
- If build fails, try using the Ubuntu-based image: `Dockerfile.ubuntu`
- For Alpine issues, the repositories are automatically updated to use alternative mirrors

### No Audio Input
- Ensure your microphone is working on the host system
- Check PulseAudio is running: `pulseaudio --check`
- Verify audio devices are accessible: `arecord -l`

### No System Tray Icon
- Ensure X11 forwarding is working: `xhost +local:docker`
- Check DISPLAY variable: `echo $DISPLAY`
- Verify desktop environment supports system tray

### Permission Denied Errors
- Run with `--privileged` flag
- Ensure user is in audio group on host system
- Check X11 permissions: `xauth list`

### Alpine Repository Issues
If you encounter Alpine repository warnings:
```
WARNING: opening from cache https://dl-cdn.alpinelinux.org/alpine/v3.18/main: No such file or directory
```
The Dockerfile automatically handles this by switching to alternative mirrors.

## Development

### Custom Model
To use a different Vosk model:
1. Modify the `MODEL_PATH` in `voice_typing.py`
2. Update the volume mount in docker-compose.yml
3. Rebuild the image

### Dependencies
Python dependencies are managed via `requirements.txt` and installed at build time for reliability.

### Choosing Base Image
- Use **Alpine** (default) for smaller images and production deployments
- Use **Ubuntu** for development or when compatibility is crucial
- Both images provide identical functionality

## Security Considerations

- Container runs in privileged mode for hardware access
- Audio data processing happens locally within the container
- No network connections required for core functionality after initial setup
- Consider using rootless containers for enhanced security

## Performance Notes

- Dependencies are now installed at build time for faster startup
- Audio processing is real-time and CPU-intensive
- Memory usage depends on the Vosk model size (small model ~50MB)
- Alpine image is significantly smaller than Ubuntu (150MB vs 350MB)
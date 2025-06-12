# Ubuntu Voice to Text - Docker Setup

This document provides instructions for running the Ubuntu Voice to Text application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)
- A working audio input device (microphone)
- X11 server running (for GUI components)
- Internet connection (for downloading Python dependencies and Vosk model on first run)

## Quick Start with Docker Compose

1. **Clone the repository and navigate to the directory:**
   ```bash
   git clone https://github.com/vovka/ubuntu_voice_to_text.git
   cd ubuntu_voice_to_text
   ```

2. **Build and run the application:**
   ```bash
   # Default (Alpine-based, smaller image):
   docker-compose up --build
   
   # Alternative (Ubuntu-based):
   docker-compose --profile ubuntu up --build voice-typing-ubuntu
   ```

   The Vosk speech recognition model is automatically downloaded and cached on first run.

3. **Use the application:**
   - The application will start with a system tray icon
   - Hold `Ctrl+Shift` to activate voice recording
   - Speak while holding the keys
   - Release to process and type the recognized text

## Docker Image Options

This project provides two Docker image variants:

### Alpine-based (Default)
- **Dockerfile**: `Dockerfile` (default)
- **Image size**: ~150MB (model downloaded separately)
- **Use case**: Production deployments where size matters
- **Build**: `docker-compose up --build`

### Ubuntu-based
- **Dockerfile**: `Dockerfile.ubuntu`
- **Image size**: ~300MB (model downloaded separately)
- **Use case**: Development or when compatibility is preferred
- **Build**: `docker-compose --profile ubuntu up --build voice-typing-ubuntu`

## CI/CD Integration

The Docker image now includes the Vosk model, simplifying CI/CD pipelines.

### GitHub Actions / CI Pipeline Setup
```yaml
- name: Build and Test Docker Image
  run: |
    docker-compose build
    # Add your test commands here
```

### Manual CI Setup
```bash
# Build and run - no model download required
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
  -v ./vosk-models:/models:rw \
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

The Vosk speech recognition model is automatically managed by the container:
1. On first run, the model is downloaded automatically from the internet
2. The model is cached in the `./vosk-models` directory on the host
3. Subsequent runs use the cached model, making startup faster
4. No manual intervention is required

**Model Location**: The model is stored at `/models/vosk-model-small-en-us-0.15` within the container.

**Model Persistence**: The `./vosk-models` directory persists the model across:
- Container restarts
- Container rebuilds  
- Host system reboots

**Model Configuration**: To use a different model, modify the `MODEL_PATH` in `voice_typing.py`. The entrypoint will automatically download the new model.

### Permissions

The container runs in privileged mode to access audio hardware. For enhanced security in production:
1. Use specific device permissions instead of privileged mode
2. Create a dedicated user with audio group membership
3. Use security contexts to limit capabilities

## Troubleshooting

### Model Download Failed
```
❌ Failed to download Vosk model after 3 attempts
```
**Solution**: 
1. Check your internet connection
2. Verify the model URL is accessible
3. Ensure the `./vosk-models` directory is writable
4. For offline environments, pre-download the model:
   ```bash
   mkdir -p ./vosk-models
   cd ./vosk-models
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip
   ```

### Model Directory Permission Issues
If you see permission errors related to the model directory:
1. Ensure the current user has write access to the project directory
2. Check Docker permissions: `ls -la ./vosk-models`
3. If needed, fix permissions: `sudo chown -R $USER:$USER ./vosk-models`

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
2. Update the Dockerfile to download your preferred model
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
- Vosk model is included in the image, eliminating runtime downloads
- Audio processing is real-time and CPU-intensive
- Memory usage depends on the Vosk model size (small model ~50MB)
- Alpine image is significantly smaller than Ubuntu (~200MB vs ~400MB including model)
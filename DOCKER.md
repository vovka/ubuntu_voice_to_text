# Ubuntu Voice to Text - Docker Setup

This document provides instructions for running the Ubuntu Voice to Text application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)
- A working audio input device (microphone)
- X11 server running (for GUI components)
- Internet connection (for downloading Python dependencies; Vosk model is included in the image)

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

   The Vosk speech recognition model is now included in the Docker image, so no separate download is required.

3. **Use the application:**
   - The application will start with a system tray icon
   - Hold `Ctrl+Shift` to activate voice recording
   - Speak while holding the keys
   - Release to process and type the recognized text

## Docker Image Options

This project provides two Docker image variants:

### Alpine-based (Default)
- **Dockerfile**: `Dockerfile` (default)
- **Image size**: ~200MB (includes Vosk model)
- **Use case**: Production deployments where size matters
- **Build**: `docker-compose up --build`

### Ubuntu-based
- **Dockerfile**: `Dockerfile.ubuntu`
- **Image size**: ~400MB (includes Vosk model)
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

The Vosk speech recognition model is now included directly in the Docker image:
1. The model is downloaded and installed during the Docker build process
2. No external volume mounting is required
3. If network access fails during build, the container will include a placeholder with instructions

**Model Location**: The model is installed at `/opt/vosk-model-small-en-us-0.15` within the container.

**Model Configuration**: To use a different model, modify the `MODEL_PATH` in `voice_typing.py` and rebuild the Docker image.

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
1. This should not occur with the new image as the model is built-in
2. If it does occur, rebuild the Docker image: `docker-compose build --no-cache`
3. Check if there were network issues during the build process

### Model Download Failed During Build
If you see a message about model download failure:
1. The container will start but may not function without a model
2. You can manually download the model and rebuild with: `./download-model.sh && docker-compose build --no-cache`
3. Ensure internet connectivity during Docker build

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
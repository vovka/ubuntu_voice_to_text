# Ubuntu Voice to Text - Docker Setup

This document provides instructions for running the Ubuntu Voice to Text application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)
- A working audio input device (microphone)
- X11 server running (for GUI components)
- Internet connection (for downloading Python dependencies and Vosk model)

## Important Notes

Due to sandboxed environments and network restrictions, some Python dependencies are installed at runtime rather than build time. The first container startup may take a few minutes while dependencies are downloaded and installed.

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
   docker-compose up --build
   ```

4. **Use the application:**
   - The application will start with a system tray icon
   - Hold `Ctrl+Shift` to activate voice recording
   - Speak while holding the keys
   - Release to process and type the recognized text

## Manual Docker Commands

### Building the Image

```bash
docker build -t ubuntu-voice-to-text .
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

### Permissions

The container runs in privileged mode to access audio hardware. For enhanced security in production:
1. Use specific device permissions instead of privileged mode
2. Create a dedicated user with audio group membership
3. Use security contexts to limit capabilities

## Runtime Dependencies

Python dependencies are installed at container startup for maximum compatibility:
- sounddevice - Audio input/output
- vosk - Speech recognition
- pyaudio - Audio interface
- keyboard - Hotkey detection
- pynput - Input simulation
- pystray - System tray icon
- pillow - Image processing

## Troubleshooting

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

### Dependency Installation Issues
- Ensure internet connectivity during first run
- Check PyPI accessibility
- Dependencies are cached after first successful installation

### Model Download Issues
- The Vosk model must be downloaded separately using `./download-model.sh`
- For offline environments, download manually and place in `vosk-model/` directory
- Alternative: mount local model directory

## Development

### Custom Model
To use a different Vosk model:
1. Modify the `MODEL_PATH` in `voice_typing.py`
2. Update the volume mount in docker-compose.yml
3. Rebuild the image

### Dependencies
Python dependencies are managed via `requirements.txt`. To add new dependencies:
1. Update `requirements.txt`
2. Dependencies will be installed at next container startup

## Security Considerations

- Container runs in privileged mode for hardware access
- Audio data processing happens locally within the container
- No network connections required for core functionality after initial setup
- Consider using rootless containers for enhanced security

## Performance Notes

- First startup may be slower due to dependency installation
- Audio processing is real-time and CPU-intensive
- Memory usage depends on the Vosk model size (small model ~50MB)
- Dependencies are cached for subsequent runs
# Ubuntu Voice to Text

A system tray voice-to-text application for Ubuntu that enables hands-free text input through speech recognition using global hotkeys. The application runs in the background and provides voice-to-text conversion that works across all applications without requiring focus.

## Features

- **Voice Recognition**: Uses Vosk for offline speech recognition
- **Global Hotkey Activation**: Hold Ctrl+Shift to activate voice recording (works outside focused applications)
- **System Tray Integration**: Convenient tray icon for status monitoring and control
- **Real-time Processing**: Immediate text typing after speech recognition
- **Cross-Application Support**: Works in any application through keyboard input simulation
- **No Internet Required**: Offline operation after initial setup

## Target Operating System

This application is specifically designed for:
- **Ubuntu 22.04.2 LTS** (primary target)
- **Ubuntu 20.04+ and compatible Linux distributions** (broader compatibility)
- **X11 desktop environment** (required for system tray and input simulation)

## How the App Interacts with the OS

### System Tray Integration
- Creates a persistent system tray icon that changes color based on application state
- Provides visual feedback for idle (gray), listening (green), and processing (blue) states
- Integrates with desktop environments that support system tray (GNOME, KDE, XFCE, etc.)

### Global Hotkey Listening
- Monitors keyboard input system-wide using the `keyboard` library
- Detects Ctrl+Shift key combination regardless of which application has focus
- Works across all desktop applications without requiring focus or permission per app

### Microphone/Audio Input Capture
- Accesses system audio devices through ALSA/PulseAudio
- Uses `sounddevice` and `pyaudio` libraries for real-time audio capture
- Requires read access to `/dev/snd` audio devices
- Supports standard microphone configurations

### Output Injection
- **Keyboard Input Simulation**: Uses `pynput` library to simulate keyboard typing
- **Direct Text Insertion**: Injects recognized text at the current cursor position
- **Cross-Application Compatibility**: Works with any application that accepts keyboard input
- **X11 Integration**: Utilizes X11 display server for input event injection

## Installation with Docker

Docker provides the easiest and most reliable way to run the application with all dependencies pre-configured.

### Prerequisites
- **Docker** (version 20.10+)
- **Docker Compose** (version 1.29+)
- **Working microphone**
- **X11 desktop environment**

### Step-by-Step Installation

1. **Install Docker and Docker Compose** (if not already installed):
   ```bash
   # Update package list
   sudo apt update
   
   # Install Docker
   sudo apt install docker.io docker-compose
   
   # Add user to docker group (logout/login required)
   sudo usermod -aG docker $USER
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/vovka/ubuntu_voice_to_text.git
   cd ubuntu_voice_to_text
   ```

3. **Download the Vosk speech recognition model:**
   ```bash
   ./download-model.sh
   ```

4. **Set required environment variables:**
   ```bash
   export UID=$(id -u)
   export GID=$(id -g)
   export USER=$(whoami)
   ```

5. **Enable X11 forwarding for Docker:**
   ```bash
   xhost +local:docker
   ```

6. **Run the application:**
   ```bash
   # Default Alpine-based image (smaller, faster)
   docker-compose up --build
   
   # Alternative Ubuntu-based image (more compatible)
   docker-compose --profile ubuntu up --build voice-typing-ubuntu
   ```

### Environment Variables
- `DISPLAY`: X11 display server (automatically set)
- `PULSE_RUNTIME_PATH`: PulseAudio socket path
- `XDG_RUNTIME_DIR`: User runtime directory
- `XAUTHORITY`: X11 authentication file path

## Docker/Audio Device Access

Docker requires special configuration to access system audio devices and display server. This section explains how Docker gains access to these resources.

### Audio Device Access Methods

#### 1. ALSA Device Mounting
- **Method**: Direct device file mounting
- **Implementation**: `-v /dev/snd:/dev/snd:rw` and `--device /dev/snd:/dev/snd`
- **Security**: Requires privileged mode for hardware access
- **Compatibility**: Works with most audio configurations

#### 2. PulseAudio Socket Sharing
- **Method**: Unix socket sharing between host and container
- **Implementation**: `-v /run/user/1000/pulse:/run/user/1000/pulse:rw`
- **Benefits**: Better audio isolation and user-specific audio sessions
- **Requirements**: PulseAudio running on host system

### Sample Docker Compose Configuration

```yaml
version: '3.8'

services:
  voice-typing:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ubuntu-voice-to-text
    # Host networking for seamless X11 and audio communication
    network_mode: host
    # Privileged mode required for audio device access
    privileged: true
    # Run as current user to maintain permissions
    user: "${UID}:${GID}"
    environment:
      # X11 display forwarding
      - DISPLAY=${DISPLAY}
      # PulseAudio configuration
      - PULSE_RUNTIME_PATH=/run/user/1000/pulse
      - XDG_RUNTIME_DIR=/run/user/1000
      # X11 authentication
      - XAUTHORITY=/home/${USER}/.Xauthority
    volumes:
      # X11 socket for GUI access (system tray)
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      # PulseAudio socket for audio access
      - /run/user/1000/pulse:/run/user/1000/pulse:rw
      # Direct audio device access
      - /dev/snd:/dev/snd:rw
      # Vosk model directory (must be downloaded first)
      - ./vosk-model:/opt/vosk-model-small-en-us-0.15:ro
      # X11 authentication file
      - /home/${USER}/.Xauthority:/home/${USER}/.Xauthority:rw
    devices:
      # Audio hardware devices
      - /dev/snd:/dev/snd
    stdin_open: true
    tty: true
    restart: unless-stopped
```

### Security and Usability Considerations

#### Security Implications
- **Privileged Mode**: Required for audio access but increases attack surface
- **Device Mounting**: Direct hardware access bypasses some container isolation
- **Host Networking**: Reduces network isolation for X11 compatibility
- **X11 Forwarding**: Allows container to interact with host display server

#### Usability Benefits
- **Seamless Audio**: No audio configuration required inside container
- **System Tray Integration**: Direct access to desktop notification area
- **Global Hotkeys**: Keyboard monitoring works across all applications
- **Persistent Model**: Vosk model persists between container restarts

#### Alternative Configurations
For enhanced security in production environments:
1. **Non-privileged audio**: Use PulseAudio server mode
2. **Network isolation**: Configure specific port forwarding instead of host mode
3. **Limited device access**: Mount only specific audio device nodes

## Manual Installation (Alternative)

For users who prefer to run the application directly on the host system:

1. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv xdotool pulseaudio alsa-utils portaudio19-dev python3-dev build-essential wget unzip
   ```

2. **Run the setup script:**
   ```bash
   ./voice_typing.sh
   ```

## Usage Example

### Starting the Application

1. **Using Docker (Recommended):**
   ```bash
   cd ubuntu_voice_to_text
   docker-compose up --build
   ```

2. **Manual Installation:**
   ```bash
   cd ubuntu_voice_to_text
   ./voice_typing.sh
   ```

### Using Voice-to-Text

1. **Verify System Tray Icon**: Look for a circular icon in your system tray
   - Gray circle = Application ready, waiting for input
   - The icon should appear within 5-10 seconds of startup

2. **Activate Voice Recording**: 
   - Hold down **Ctrl+Shift** simultaneously
   - Icon turns **green** indicating active listening
   - You'll see the title change to "Voice Typing: ON"

3. **Speak Your Text**:
   - Speak clearly and at normal volume
   - Continue holding Ctrl+Shift while speaking
   - Optimal distance: 6-12 inches from microphone

4. **Complete Recognition**:
   - Release **Ctrl+Shift** keys
   - Icon turns **blue** indicating processing
   - Recognized text will be typed at current cursor position
   - Icon returns to **gray** when ready for next input

### Example Workflow

```bash
# Terminal example - dictating a git commit message
git commit -m "   # Hold Ctrl+Shift and say "Add new feature for user authentication"
# Result: git commit -m "Add new feature for user authentication"

# Text editor example - writing documentation
# Place cursor in document, hold Ctrl+Shift, speak:
# "This function processes user input and returns a formatted string"
# Text appears where cursor was positioned
```

### Expected Behavior

- **Response Time**: 1-3 seconds from key release to text appearance
- **Accuracy**: 85-95% for clear speech in quiet environments
- **Text Length**: Works best with phrases of 1-20 words
- **Applications**: Compatible with any text field (browsers, editors, terminals, etc.)

## Configuration

The application can be configured by modifying `voice_typing.py`:

- **Model Path**: Change `MODEL_PATH` to use a different Vosk model
- **Sample Rate**: Adjust `SAMPLE_RATE` for audio quality
- **Hotkey Combo**: Modify `HOTKEY_COMBO` to use different activation keys

## Dependencies

### Python Requirements
- **Python 3.8+** (tested with Python 3.8, 3.9, 3.10, 3.11)
- **Virtual environment** support (recommended)

### Main Python Libraries
- **`vosk`** - Offline speech recognition engine (primary component)
- **`sounddevice`** - Audio input/output interface
- **`pyaudio`** - Cross-platform audio I/O library
- **`keyboard`** - Global hotkey detection and monitoring
- **`pynput`** - Cross-platform input simulation for text insertion
- **`pystray`** - System tray icon creation and management
- **`pillow (PIL)`** - Image processing for tray icon graphics

### System Dependencies (Ubuntu/Debian)
```bash
# Core Python development
python3-dev          # Python development headers
python3-venv         # Virtual environment support
build-essential      # Compilation tools (gcc, make, etc.)

# Audio system packages
pulseaudio          # Audio server
alsa-utils          # ALSA utilities
portaudio19-dev     # PortAudio development headers

# X11 and desktop integration
xdotool             # X11 automation tool
python3-pil         # PIL/Pillow system package

# Utility packages
wget                # Download tool
unzip               # Archive extraction
```

### Docker Dependencies
When using Docker, all dependencies are automatically included:
- **Docker Engine** 20.10+
- **Docker Compose** 1.29+
- **Host audio system** (PulseAudio or ALSA)
- **X11 server** (for system tray integration)

### Model Dependencies
- **Vosk Model**: ~40MB download (vosk-model-small-en-us-0.15)
- **Internet connection**: Required only for initial model download
- **Storage**: ~50MB for model and application files

## Configuration

The application can be configured by modifying `voice_typing.py`:

- **Model Path**: Change `MODEL_PATH` to use a different Vosk model
- **Sample Rate**: Adjust `SAMPLE_RATE` for audio quality (default: 16000 Hz)
- **Hotkey Combo**: Modify `HOTKEY_COMBO` to use different activation keys (default: Ctrl+Shift)

### Configuration Examples

```python
# In voice_typing.py, class Config:
MODEL_PATH = "/opt/vosk-model-small-en-us-0.15"  # Model location
SAMPLE_RATE = 16000                              # Audio sample rate
HOTKEY_COMBO = {keyboard.Key.ctrl, keyboard.Key.shift}  # Activation keys
```

## Docker Support Summary

This application is fully containerized with Docker support:

- **Easy deployment** with Docker Compose
- **Isolated environment** with all dependencies pre-installed
- **Audio and display forwarding** for seamless host integration
- **Volume mounting** for model and configuration persistence
- **Two image variants**: Alpine (smaller) and Ubuntu (more compatible)

For comprehensive Docker setup instructions, see [DOCKER.md](DOCKER.md).

## Troubleshooting

### Audio Issues
- Ensure microphone is working: `arecord -d 5 test.wav && aplay test.wav`
- Check audio permissions and device availability
- Verify PulseAudio is running: `pulseaudio --check`

### System Tray Issues
- Ensure desktop environment supports system tray
- Check X11 display forwarding (for Docker)
- Verify DISPLAY environment variable

### Voice Recognition Issues
- Speak clearly and at normal volume
- Ensure Vosk model is properly downloaded and extracted
- Check model path configuration

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is open source. Please check the repository for license information.

## Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) for the speech recognition engine
- The Python audio and GUI library communities
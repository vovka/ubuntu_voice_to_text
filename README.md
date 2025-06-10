# Ubuntu Voice to Text

A simple voice-to-text application for Ubuntu that provides hands-free text input using speech recognition.

## Features

- **Voice Recognition**: Uses Vosk for offline speech recognition
- **Hotkey Activation**: Hold Ctrl+Shift to activate voice recording
- **System Tray Integration**: Convenient tray icon for status monitoring
- **Real-time Processing**: Immediate text typing after speech recognition
- **No Internet Required**: Offline operation after initial setup

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vovka/ubuntu_voice_to_text.git
   cd ubuntu_voice_to_text
   ```

2. **Download the speech recognition model:**
   ```bash
   ./download-model.sh
   ```

3. **Run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

For detailed Docker setup instructions, see [DOCKER.md](DOCKER.md).

### Manual Installation

1. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv xdotool pulseaudio alsa-utils portaudio19-dev python3-dev build-essential wget unzip
   ```

2. **Run the setup script:**
   ```bash
   ./voice_typing.sh
   ```

## Usage

1. **Start the application** (Docker or manual installation)
2. **Look for the system tray icon** (circle that changes color based on status)
3. **Hold Ctrl+Shift** to activate voice recording (icon turns green)
4. **Speak clearly** while holding the keys
5. **Release the keys** to process speech and type the recognized text

### Status Indicators

- **Gray**: Idle, ready for input
- **Green**: Actively listening/recording
- **Blue**: Processing speech

## Configuration

The application can be configured by modifying `voice_typing.py`:

- **Model Path**: Change `MODEL_PATH` to use a different Vosk model
- **Sample Rate**: Adjust `SAMPLE_RATE` for audio quality
- **Hotkey Combo**: Modify `HOTKEY_COMBO` to use different activation keys

## Requirements

### System Requirements

- Ubuntu 22.04 or compatible Linux distribution
- Working microphone
- X11 desktop environment (for system tray and xdotool)
- Audio system (PulseAudio or ALSA)

### Python Dependencies

- `sounddevice` - Audio input/output
- `vosk` - Speech recognition engine
- `pyaudio` - Audio interface
- `keyboard` - Hotkey detection
- `pynput` - Input simulation
- `pystray` - System tray icon
- `pillow` - Image processing

## Docker Support

This application is fully containerized with Docker support:

- **Easy deployment** with Docker Compose
- **Isolated environment** with all dependencies
- **Audio and display forwarding** for seamless operation
- **Volume mounting** for model and configuration persistence

See [DOCKER.md](DOCKER.md) for comprehensive Docker setup and usage instructions.

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

## Development

### Running Tests

This project includes a comprehensive test suite using pytest. Tests can be run locally or via Docker.

#### Local Testing

1. **Install test dependencies:**
   ```bash
   pip install pytest pytest-cov coverage flake8 black
   ```

2. **Run tests:**
   ```bash
   # Run all tests with coverage
   pytest tests/ --cov=. --cov-report=term-missing -v
   
   # Run only smoke tests
   pytest tests/test_smoke.py -v
   ```

3. **Run linting:**
   ```bash
   # Check code style
   flake8 . --max-line-length=88
   
   # Check code formatting
   black --check --diff .
   
   # Auto-format code
   black .
   ```

#### Docker Testing

Run tests in an isolated Docker container:

```bash
# Run tests
docker-compose --profile test run --rm test

# Run linting
docker-compose --profile test run --rm lint

# Format code
docker-compose --profile test run --rm format

# Run all checks (build and test in one command)
docker-compose build && docker-compose --profile test run --rm test && docker-compose --profile test run --rm lint
```

#### CI/CD

The project includes GitHub Actions workflow that automatically:
- Tests on multiple Python versions (3.8-3.12)
- Runs linting with flake8
- Checks code formatting with black
- Generates coverage reports

### Code Quality

- **Test Framework**: pytest with coverage reporting
- **Linting**: flake8 for code quality checks
- **Formatting**: black for consistent code style
- **Coverage**: Aim for high test coverage of core functionality

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

Before submitting a pull request:
1. Run the test suite: `pytest tests/`
2. Check code style: `flake8 . --max-line-length=88`
3. Format code: `black .`
4. Ensure all CI checks pass

## License

This project is open source. Please check the repository for license information.

## Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) for the speech recognition engine
- The Python audio and GUI library communities
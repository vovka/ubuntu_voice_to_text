# Ubuntu Voice to Text

A simple voice-to-text application for Ubuntu that provides hands-free text input using speech recognition.

## Features

- **Voice Recognition**: Supports multiple speech recognition engines:
  - **Vosk**: Offline speech recognition (default)
  - **OpenAI Whisper**: Cloud-based speech recognition via API
- **Hotkey Activation**: Press and release Ctrl+Shift to toggle voice recording
- **Auto-Disable**: Automatically stops listening after 5 seconds of silence
- **System Tray Integration**: Convenient tray icon for status monitoring
- **Real-time Processing**: Immediate text typing after speech recognition
- **Configurable Backend**: Switch between recognition sources via environment variables

## Requirements

- **Python 3.12** or later
- **Ubuntu** (tested on Ubuntu 20.04+, but should work on other Linux distributions)
- **Audio system** (PulseAudio/ALSA)

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vovka/ubuntu_voice_to_text.git
   cd ubuntu_voice_to_text
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

The Docker container will automatically download and cache the Vosk speech recognition model on first run. The model is persisted in the `./vosk-models` directory, so subsequent runs will be faster.

For detailed Docker setup instructions, see [DOCKER.md](DOCKER.md).

### Manual Installation

1. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv xdotool pulseaudio alsa-utils portaudio19-dev python3-dev build-essential wget unzip ffmpeg libsndfile1
   ```

2. **Install Poetry:**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   # Add Poetry to PATH
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Install Python dependencies:**
   ```bash
   poetry install
   ```

4. **Download the Vosk model (required for manual installation):**
   ```bash
   ./download-model.sh
   ```

5. **Set the model path and run the application:**
   ```bash
   export VOSK_MODEL_PATH="$(pwd)/vosk-model-small-en-us-0.15"
   poetry run python main.py
   ```

## Usage

1. **Start the application** (Docker or manual installation)
2. **Look for the system tray icon** (circle that changes color based on status)
3. **Press and release Ctrl+Shift** to activate voice recording (icon turns green)
4. **Speak clearly** after releasing the keys
5. **Stop recording** by either:
   - **Manual**: Press Ctrl+Shift again to immediately stop recording
   - **Automatic**: Wait 5 seconds after your last speech and recording will automatically stop

### Status Indicators

- **Gray**: Idle, ready for input
- **Green**: Actively listening/recording
- **Blue**: Processing speech

## Configuration

The application can be configured via environment variables or by modifying `main.py`:

### Voice Recognition Source

Choose between different speech recognition engines:

```bash
# Use Vosk (offline, default)
export RECOGNITION_SOURCE=vosk

# Use OpenAI Whisper (requires API key)
export RECOGNITION_SOURCE=whisper
export OPENAI_API_KEY=your_openai_api_key_here
export WHISPER_MODEL=whisper-1  # Optional, defaults to whisper-1
```

#### Using with Docker

Set environment variables in your shell or create a `.env` file:

```bash
# Copy the example configuration file
cp .env.example .env
# Edit .env file with your settings
```

Example `.env` file:
```bash
# .env file
RECOGNITION_SOURCE=whisper
OPENAI_API_KEY=sk-your-api-key-here
WHISPER_MODEL=whisper-1
```

Then run:
```bash
docker-compose up --build
```

### Legacy Configuration

You can also configure by modifying `main.py`:

- **Model Path**: Change `MODEL_PATH` to use a different Vosk model (Vosk only)
- **Sample Rate**: Adjust `SAMPLE_RATE` for audio quality
- **Hotkey Combo**: Modify `HOTKEY_COMBO` to use different activation keys

### Vosk Model Configuration

The application uses the **vosk-model-small-en-us-0.15** model by default, which provides:
- **Language**: English (US)
- **Size**: ~50MB
- **Quality**: Optimized for size and reasonable accuracy

#### Environment Variables

```bash
# Vosk model path (for manual installation)
export VOSK_MODEL_PATH="/path/to/vosk-model-small-en-us-0.15"

# Recognition source selection
export RECOGNITION_SOURCE=vosk  # or whisper

# OpenAI Whisper configuration
export OPENAI_API_KEY=sk-your-api-key-here
export WHISPER_MODEL=whisper-1
```

#### Docker Model Management

When using Docker, the model is automatically managed:
- **First run**: The model is downloaded automatically and cached in `./vosk-models/`
- **Subsequent runs**: The cached model is used, making startup faster
- **Model persistence**: The model persists across container rebuilds and restarts
- **No host dependency**: No manual setup required on the host system

#### Manual Model Management

To use a different model:
1. Update the `MODEL_PATH` in `main.py`
2. For Docker: The entrypoint will automatically download the new model
3. For manual installation: Download the model manually and update the path

Available models can be found at: https://alphacephei.com/vosk/models

### OpenAI Whisper Configuration

To use OpenAI Whisper ASR instead of Vosk:

1. **Get an OpenAI API key** from [OpenAI Platform](https://platform.openai.com/)

2. **Set environment variables:**
   ```bash
   export RECOGNITION_SOURCE=whisper
   export OPENAI_API_KEY=sk-your-api-key-here
   export WHISPER_MODEL=whisper-1  # Optional, defaults to whisper-1
   ```

3. **Run the application** (Docker or manual installation)

#### Whisper vs Vosk Comparison

| Feature | Vosk | OpenAI Whisper |
|---------|------|----------------|
| **Internet Required** | No | Yes |
| **Setup Complexity** | Model download required | API key only |
| **Accuracy** | Good | Excellent |
| **Processing Speed** | Real-time | Near real-time |
| **Privacy** | Complete (offline) | Data sent to OpenAI |
| **Cost** | Free | Pay per usage |
| **Language Support** | Limited by model | 90+ languages |

#### Whisper API Costs

OpenAI Whisper API charges $0.006 per minute of audio. A typical voice input session (5-10 seconds) costs less than $0.001.

## Requirements

### System Requirements

- Ubuntu 22.04 or compatible Linux distribution
- Working microphone
- X11 desktop environment (for system tray and xdotool)
- Audio system (PulseAudio or ALSA)

### Python Dependencies

- `sounddevice` - Audio input/output
- `vosk` - Speech recognition engine (offline)
- `openai` - OpenAI Whisper API client (cloud-based)
- `sounddevice` - Audio input/output
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

1. **Install dependencies (including dev dependencies):**
   ```bash
   poetry install
   ```

2. **Run tests:**
   ```bash
   # Run all tests with coverage
   poetry run pytest tests/ --cov=. --cov-report=term-missing -v

   # Run only smoke tests
   poetry run pytest tests/test_smoke.py -v
   ```

3. **Run linting:**
   ```bash
   # Check code style
   poetry run flake8 . --max-line-length=88

   # Check code formatting
   poetry run black --check --diff .

   # Auto-format code
   poetry run black .
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
- Tests on Python 3.12
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

### Development Setup

1. **Install Poetry:**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Before submitting a pull request:**
   ```bash
   # Run the test suite
   poetry run pytest tests/

   # Check code style
   poetry run flake8 . --max-line-length=88

   # Format code
   poetry run black .
   ```

4. Ensure all CI checks pass

## License

This project is open source. Please check the repository for license information.

## Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) for the speech recognition engine
- The Python audio and GUI library communities

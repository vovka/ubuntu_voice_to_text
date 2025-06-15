# Centralized Configuration Management

## Overview

The voice typing system now uses centralized configuration management to decouple business logic from direct environment variable access. This ensures:

- Single point of configuration loading
- Immutable configuration after initialization
- Testable configuration management
- Clear separation between configuration loading and business logic

## Components

### ConfigurationLoader

The `ConfigurationLoader` class provides a centralized way to load configuration from environment variables, files, or other sources.

```python
from voice_typing import ConfigurationLoader

# Load configuration from environment variables
config_dict = ConfigurationLoader.load_configuration()

# Future: Load from configuration file
file_config = ConfigurationLoader.load_from_file("config.json")

# Merge configurations (later configs override earlier ones)
merged = ConfigurationLoader.merge_configurations(
    default_config, file_config, env_config
)
```

### Config Class

The `Config` class now accepts configuration values via constructor instead of reading environment variables directly:

```python
from voice_typing import Config, ConfigurationLoader

# Use default configuration loading
config = Config()  # Internally uses ConfigurationLoader

# Use custom configuration
custom_config = {
    "sample_rate": 8000,
    "recognition_source": "whisper",
    "openai_api_key": "your-api-key"
}
config = Config(custom_config)
```

## Configuration Keys

| Key | Environment Variable | Default | Description |
|-----|---------------------|---------|-------------|
| `model_path` | `VOSK_MODEL_PATH` | `/models/vosk-model-small-en-us-0.15` | Path to Vosk model |
| `sample_rate` | - | `16000` | Audio sample rate |
| `recognition_source` | `RECOGNITION_SOURCE` | `vosk` | Recognition backend (vosk/whisper) |
| `openai_api_key` | `OPENAI_API_KEY` | `None` | OpenAI API key for Whisper |
| `whisper_model` | `WHISPER_MODEL` | `gpt-4o-transcribe` | Whisper model name |
| `hotkey_combo` | - | Win+Shift | Hotkey combination |

## Usage in Applications

### Main Application

```python
from voice_typing import ConfigurationLoader, Config, AudioProcessor, GlobalState

# Load configuration once at startup
config_dict = ConfigurationLoader.load_configuration()

# Override specific values if needed
config_dict["sample_rate"] = 22050  # Custom sample rate

# Create config object
config = Config(config_dict)

# Pass to components
state_ref = GlobalState()
audio_processor = AudioProcessor(config, state_ref)
```

### Testing

```python
# Test with custom configuration
test_config = {
    "recognition_source": "mock",
    "sample_rate": 8000,
    "model_path": "/test/model"
}
config = Config(test_config)

# Configuration is immutable after creation
# Environment changes won't affect the config object
```

## Migration Notes

### Before (Direct Environment Access)

```python
import os

class SomeModule:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")  # Direct access
        self.model = os.getenv("WHISPER_MODEL", "default")
```

### After (Dependency Injection)

```python
class SomeModule:
    def __init__(self, config):
        self.api_key = config.OPENAI_API_KEY  # From injected config
        self.model = config.WHISPER_MODEL
```

## Benefits

1. **Centralized**: All configuration loading happens in one place
2. **Testable**: Easy to inject test configurations
3. **Immutable**: Configuration doesn't change after initialization
4. **Decoupled**: Business logic doesn't know about environment variables
5. **Extensible**: Easy to add new configuration sources (files, databases, etc.)

## Future Enhancements

- Configuration file support (JSON, YAML, INI)
- Configuration validation
- Configuration change notifications
- Environment-specific configuration profiles
- Configuration caching and optimization
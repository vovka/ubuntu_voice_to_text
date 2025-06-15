"""
Smoke tests to validate the test setup and basic functionality.
"""

import sys
import os


def test_smoke_always_passes():
    """A simple test that always passes to validate test setup."""
    assert True


def test_python_version():
    """Test that Python version is compatible."""
    assert sys.version_info >= (3, 8)


def test_main_module_imports():
    """Test that the main voice_typing module can be imported."""
    # Add the project root to the path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

    try:
        import voice_typing

        assert hasattr(voice_typing, "Config")
        assert hasattr(voice_typing, "AudioProcessor")
        assert hasattr(voice_typing, "PipelineVoiceTyping")
        assert hasattr(voice_typing, "BasicStateManager")
        assert hasattr(voice_typing, "TrayIconManager")
        assert hasattr(voice_typing, "HotkeyManager")
    except ImportError as e:
        # If import fails due to missing dependencies,
        # that's expected in CI environment
        expected_deps = [
            "vosk",
            "sounddevice",
            "keyboard",
            "pynput",
            "pystray",
            "pillow",
        ]
        if any(dep in str(e).lower() for dep in expected_deps):
            # Skip this test in CI where dependencies might not be available
            import pytest

            pytest.skip(f"Skipping due to missing dependencies: {e}")
        else:
            raise


def test_config_class():
    """Test that the Config class has expected attributes."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

    try:
        from voice_typing import Config

        config = Config()
        assert hasattr(config, "MODEL_PATH")
        assert hasattr(config, "SAMPLE_RATE")
        assert hasattr(config, "HOTKEY_COMBO")
        assert config.SAMPLE_RATE == 16000
    except ImportError as e:
        import pytest

        pytest.skip(f"Skipping due to missing dependencies: {e}")




"""
Test CLI entry point functionality.
"""

import importlib.util
from pathlib import Path


def test_main_module_has_main_function():
    """Test that main.py has a main function for the CLI entry point."""
    main_file = Path(__file__).parent.parent / "main.py"
    content = main_file.read_text()
    
    assert "def main():" in content
    assert "if __name__ == \"__main__\":" in content
    assert "main()" in content


def test_main_function_can_be_imported():
    """Test that the main function can be imported from main.py."""
    import sys
    import os
    
    # Add the project root to the path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        import main
        assert hasattr(main, 'main')
        assert callable(main.main)
    finally:
        sys.path.remove(str(project_root))


def test_pyproject_toml_has_script_entry():
    """Test that pyproject.toml defines the CLI entry point."""
    pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_file.read_text()
    
    assert "[tool.poetry.scripts]" in content
    assert "ubuntu-voice-to-text = \"main:main\"" in content
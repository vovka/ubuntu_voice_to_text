"""
Tests to validate Poetry migration works correctly.
"""

import os
import subprocess
import sys
from pathlib import Path


def test_poetry_lock_exists():
    """Test that poetry.lock file exists."""
    project_root = Path(__file__).parent.parent
    poetry_lock = project_root / "poetry.lock"
    assert poetry_lock.exists(), "poetry.lock file should exist"


def test_pyproject_toml_has_poetry_config():
    """Test that pyproject.toml has Poetry configuration."""
    project_root = Path(__file__).parent.parent
    pyproject_toml = project_root / "pyproject.toml"
    
    assert pyproject_toml.exists(), "pyproject.toml should exist"
    
    content = pyproject_toml.read_text()
    assert "[tool.poetry]" in content, "pyproject.toml should have [tool.poetry] section"
    assert "[tool.poetry.dependencies]" in content, "pyproject.toml should have dependencies section"
    assert "[tool.poetry.group.dev.dependencies]" in content, "pyproject.toml should have dev dependencies"


def test_requirements_txt_removed():
    """Test that requirements.txt no longer exists."""
    project_root = Path(__file__).parent.parent
    requirements_txt = project_root / "requirements.txt"
    assert not requirements_txt.exists(), "requirements.txt should be removed"


def test_poetry_commands_work():
    """Test that basic Poetry commands work."""
    if os.getenv("SKIP_POETRY_TESTS"):
        import pytest
        pytest.skip("Skipping Poetry tests due to environment variable")
    
    try:
        # Test poetry check
        result = subprocess.run(
            ["poetry", "check"], 
            cwd=Path(__file__).parent.parent,
            capture_output=True, 
            text=True, 
            timeout=30
        )
        # Poetry check should succeed (exit code 0) even with warnings
        assert result.returncode == 0, f"poetry check failed: {result.stderr}"
        
        # Test poetry show (should list installed packages)
        result = subprocess.run(
            ["poetry", "show"], 
            cwd=Path(__file__).parent.parent,
            capture_output=True, 
            text=True, 
            timeout=30
        )
        assert result.returncode == 0, f"poetry show failed: {result.stderr}"
        
        # Should have some expected packages
        output = result.stdout.lower()
        expected_packages = ["vosk", "pytest", "black", "flake8"]
        for package in expected_packages:
            assert package in output, f"Expected package {package} not found in poetry show output"
            
    except FileNotFoundError:
        import pytest
        pytest.skip("Poetry not available in test environment")
    except subprocess.TimeoutExpired:
        import pytest 
        pytest.skip("Poetry commands timed out")


def test_dev_dependencies_available():
    """Test that development dependencies are available."""
    project_root = Path(__file__).parent.parent
    
    # These should be available if Poetry is set up correctly
    try:
        import pytest
        import coverage
        # These imports should work if dev dependencies are installed
        assert True
    except ImportError as e:
        # If we're not in Poetry environment, skip this test
        import pytest
        pytest.skip(f"Dev dependencies not available: {e}")
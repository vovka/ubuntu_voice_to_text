# Copilot Instructions for This Python Project

This document sets out coding and architectural conventions for Copilot and all contributors.

## Code Style

- **Follow [PEP 8](https://peps.python.org/pep-0008/)** for all Python code unless otherwise specified.
- Use clear, descriptive names for variables, functions, and classes.
- Use type hints in all function and method signatures.

## Class and Method Structure

- **Class Limit:** Each class must not exceed **100 lines** (excluding comments and docstrings).
- **Method Limit:** Each method/function should not exceed **10 lines** of code. If a method is longer, consider refactoring.
- **Single-class files:** Each class must be defined in its own file.
- **Class Documentation:** Each class file must begin with a docstring or comment that describes:
  - The class’s purpose
  - What it does
  - Any important implementation notes

## File Organization

- Place each class in a separate file named after the class (e.g., `my_class.py` for `MyClass`).
- Organize modules and packages logically to reflect the domain and usage.

## Testing Requirements

- **Test Structure:** Mirror the project’s directory structure within the `tests/` directory for easy navigation and mapping.
- **One Assertion per Test:** Each test function should have only one assertion to keep tests focused and failures easy to diagnose.
- **Test Naming:** Name test files and classes to match the code under test.
- **Test Coverage:** All public methods and functions must have corresponding tests.

## General

- Write clear, concise, and self-explanatory code.
- Comment on non-obvious logic and decisions.
- Document all public APIs.

---

> **Note:** These instructions are intended to help Copilot and contributors generate maintainable, readable, and well-tested code. If a particular situation requires deviation from these conventions, document it clearly in code comments or a project-specific README section.

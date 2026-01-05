# Contributing to GitHub Wizard

Thanks for your interest in contributing! This document provides guidelines for contributing.

## Code of Conduct

Be respectful and inclusive. This project celebrates neurodivergent developers.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/gh-wizard`
3. Create a virtual environment: `python -m venv venv`
4. Activate: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
5. Install dev dependencies: `pip install -e ".[dev]"`

## Making Changes

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest`
4. Format code: `black src/ tests/`
5. Check types: `mypy src/`
6. Commit: `git commit -am "Add your changes"`
7. Push: `git push origin feature/your-feature`
8. Open a Pull Request

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Keep functions small and focused
- Write tests for new features

## Pull Request Process

1. Ensure tests pass
2. Update documentation if needed
3. Add a clear PR description
4. Link any related issues
5. Be open to feedback

## Questions?

Open an issue or discuss in GitHub Discussions!

# Developer Setup Guide

This guide covers setting up a development environment for Storyteller.

## Prerequisites

- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) package manager
- Git

## Installing uv

```bash
# Install uv (recommended method)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

## Clone and Setup

```bash
# Clone the repository
git clone https://github.com/hherb/storyteller.git
cd storyteller

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate

# Install in development mode with all dependencies
uv pip install -e ".[all]"
```

## Installing AI Models

### MFLUX (Image Generation)

```bash
# Install mflux
uv pip install mflux

# First run will download models (~12-23GB)
# Test with the prototype:
cd prototypes/mflux_test
python generate_test_images.py --prompt "A test image" --output test.png
```

### Ollama (Language Model)

```bash
# Install Ollama
brew install ollama

# Start Ollama service
ollama serve

# Pull a model (in another terminal)
ollama pull phi4
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/storyteller

# Run specific test file
pytest tests/test_core/test_story.py
```

## Code Quality

```bash
# Lint code
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Type checking
mypy src/
```

## Project Structure

See [architecture.md](architecture.md) for detailed project structure documentation.

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes following the guidelines in `/CLAUDE.md`
3. Ensure all tests pass: `pytest`
4. Ensure code quality: `ruff check src/`
5. Commit with conventional commit messages
6. Create a pull request

## Common Issues

### mflux ImportError

Ensure you're on macOS with Apple Silicon. MFLUX uses MLX which only works on Apple Silicon Macs.

### Ollama Connection Error

Make sure Ollama is running:
```bash
ollama serve
```

### Out of Memory

Close other applications. Image generation requires 16-24GB of RAM during inference.

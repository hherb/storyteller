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

# Install all dependencies (creates venv automatically)
uv sync --all-extras
```

That's it! `uv sync` automatically:
- Creates a `.venv` virtual environment
- Installs all dependencies from `uv.lock`
- Installs the project in editable mode

## Installing AI Models

### MFLUX (Image Generation)

```bash
# First run will download models (~12-23GB)
# Test with the prototype:
cd prototypes/mflux_test
uv sync
uv run python generate_test_images.py --prompt "A test image" --output test.png
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
uv run pytest

# Run with coverage
uv run pytest --cov=src/storyteller

# Run specific test file
uv run pytest tests/test_core/test_story.py
```

## Code Quality

```bash
# Lint code
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/

# Type checking
uv run mypy src/
```

## Project Structure

See [architecture.md](architecture.md) for detailed project structure documentation.

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes following the guidelines in `/CLAUDE.md`
3. Ensure all tests pass: `uv run pytest`
4. Ensure code quality: `uv run ruff check src/`
5. Commit with conventional commit messages
6. Create a pull request

## Common uv Commands

| Command | Description |
|---------|-------------|
| `uv sync` | Install dependencies from lockfile |
| `uv sync --all-extras` | Install with all optional dependencies |
| `uv add <package>` | Add a new dependency |
| `uv remove <package>` | Remove a dependency |
| `uv run <command>` | Run command in the virtual environment |
| `uv lock` | Update the lockfile |

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

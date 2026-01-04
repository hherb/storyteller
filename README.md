# Storyteller

An AI-powered application for creating personalized, illustrated storybooks for young children.

## Overview

Storyteller helps parents and older children collaboratively create custom storybooks for younger children (pre-reading to primary school age). The application runs entirely locally without internet connectivity after installation, ensuring privacy and offline availability.

### Key Features

- **Interactive Story Creation** - AI guides authors through the storytelling process, prompting for details, filling narrative gaps, and maintaining story structure
- **AI-Generated Illustrations** - Create engaging, child-appropriate illustrations using local image generation
- **Fully Offline** - All AI processing happens locally on your machine
- **Export to Print** - Generate print-ready PDF storybooks

### Philosophy

Rather than generating entire stories from a single prompt, Storyteller emphasizes an interactive creation process where:
- The AI asks guiding questions about characters, settings, and plot
- Authors maintain creative control while receiving assistance
- Stories develop through collaborative dialogue
- The final product reflects the author's vision, enhanced by AI

## Requirements

### Hardware

- **macOS with Apple Silicon** (M1/M2/M3/M4)
- **32GB RAM** (recommended)
- **50GB free disk space** (for AI models)

### Software

- Python 3.10+
- macOS 13.0+ (Ventura or later)

## Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/hherb/storyteller.git
cd storyteller

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e .
```

### First Run

The first run will download required AI models (~25-35GB total):
- Image generation model (FLUX via MFLUX): ~12-23GB
- Language model (via Ollama): ~8-14GB

## Project Structure

```
storyteller/
├── src/storyteller/          # Main application package
│   ├── core/                 # Story engine, book management, export
│   ├── ui/                   # Flet-based GUI components
│   └── generation/           # AI text and image generation
├── tests/                    # Test suite
├── prototypes/               # Experimental code and evaluations
│   └── mflux_test/          # Image generation quality testing
├── docs/                     # Documentation
│   ├── user/                # End-user guides
│   ├── developers/          # Developer documentation
│   ├── llm/                 # AI assistant reference
│   └── planning/            # Roadmaps and technical decisions
├── CLAUDE.md                # AI assistant guidelines
└── pyproject.toml           # Project configuration
```

## Development Status

🚧 **Early Development** - This project is in the prototyping phase.

### Current Progress

- [x] Project structure and configuration
- [x] MFLUX image generation prototype
- [ ] LLM integration for story guidance
- [ ] Flet GUI implementation
- [ ] Story engine and page management
- [ ] PDF export functionality
- [ ] macOS installer packaging

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **GUI Framework** | [Flet](https://flet.dev/) | Cross-platform Python UI |
| **Image Generation** | [MFLUX](https://github.com/filipstrand/mflux) | FLUX models on Apple Silicon |
| **Language Model** | [Ollama](https://ollama.com/) | Local LLM inference |
| **ML Framework** | [MLX](https://github.com/ml-explore/mlx) | Apple Silicon optimization |
| **Packaging** | PyInstaller + create-dmg | macOS app distribution |

## Usage

### Running Prototypes

**Test image generation quality:**

```bash
cd prototypes/mflux_test
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Generate test images
python generate_test_images.py --test-suite

# Generate single image
python generate_test_images.py --prompt "A friendly bear in the forest" --output bear.png
```

### Running the Application

*(Coming soon)*

```bash
# Start the Storyteller application
python -m storyteller
```

## Documentation

| Audience | Location | Description |
|----------|----------|-------------|
| End Users | [docs/user/](docs/user/) | Getting started, usage guides |
| Developers | [docs/developers/](docs/developers/) | Setup, architecture, contributing |
| AI Assistants | [docs/llm/](docs/llm/) | Quick reference, API patterns |
| Planning | [docs/planning/](docs/planning/) | Roadmaps, technical decisions |

## Contributing

Contributions are welcome! Please read our development guidelines in [CLAUDE.md](CLAUDE.md) for code style and architecture decisions.

### Development Setup

```bash
# Install development dependencies
uv pip install -e ".[all]"

# Run tests
pytest

# Run linting
ruff check src/

# Type checking
mypy src/
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Black Forest Labs](https://blackforestlabs.ai/) for FLUX image generation models
- [Apple MLX Team](https://github.com/ml-explore/mlx) for the MLX framework
- [MFLUX Contributors](https://github.com/filipstrand/mflux) for the Apple Silicon port
- [Flet Team](https://flet.dev/) for the Python UI framework

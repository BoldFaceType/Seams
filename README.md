# Seams

[![CI](https://github.com/BoldFaceType/Seams/actions/workflows/ci.yml/badge.svg)](https://github.com/BoldFaceType/Seams/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Connecting components seamlessly

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
pip install seams
```

## Quick Start

```python
from seams import something

# Example usage
```

## Development

### Prerequisites

- [mise](https://mise.jdx.dev/) - Runtime version manager
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### Setup

```bash
# Clone the repo
git clone https://github.com/BoldFaceType/Seams.git
cd Seams

# Install tools (mise auto-activates Python)
mise install
mise trust

# Bootstrap dev environment
make bootstrap

# Activate virtual environment
source .venv/bin/activate

# Verify setup
make ci
```

### Available Commands

```bash
make help       # Show all commands
make bootstrap  # One-time setup
make lint       # Run linter
make format     # Format code
make test       # Run tests with coverage
make test-fast  # Quick test run
make ci         # Full CI simulation
make clean      # Remove build artifacts
```

### Pre-commit Hooks

```bash
# Install hooks (one-time)
pre-commit install

# Run manually
pre-commit run --all-files
```

## License

MIT License - see [LICENSE](LICENSE) for details.

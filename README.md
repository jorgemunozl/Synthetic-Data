## Package Manager

This project uses [uv](https://github.com/astral-sh/uv) as the Python package manager for faster dependency resolution and installation.

### Installation

First, install uv:
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv

## Development Instructions
Update your development workflow sections:

```markdown
## Development

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/yourproject.git
cd yourproject

# Install dependencies
uv sync

# Activate the virtual environment (if needed)
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
## Prerequisites Section
Update your prerequisites to mention uv:

```markdown
## Prerequisites

- Python 3.8+ 
- [uv](https://github.com/astral-sh/uv) package manager

Future work !

Level 2 generator  
- Better prompting
- Better ids logic
- Use vision models
- Use of one metric
- Better pairing json png.
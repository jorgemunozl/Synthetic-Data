# 🚀 Synthetic Data Generator

An AI-powered educational content generator that creates interactive flowcharts and diagrams using advanced LangGraph workflows. This project combines OpenAI's language models with automated diagram generation to produce high-quality educational materials.

## ✨ Features

- 🤖 **AI-Powered Content Generation**: Uses OpenAI GPT models for intelligent content creation
- 📊 **Automated Flowchart Generation**: Converts text descriptions into Mermaid diagrams
- 🔄 **Iterative Quality Improvement**: Self-reflection and refinement through LangGraph workflows
- 🚀 **FastAPI Integration**: RESTful API for easy integration and deployment
- 📈 **Scalable Architecture**: Built with async/await patterns for high performance
- 🎯 **Educational Focus**: Specialized in creating learning materials and tutorials

## 🛠️ Tech Stack

- **Python 3.12+** - Core language
- **LangGraph** - Workflow orchestration and graph processing
- **LangChain** - LLM integration and prompt management
- **FastAPI** - High-performance web API framework
- **OpenAI API** - Advanced language model capabilities
- **Mermaid** - Diagram and flowchart generation
- **Pydantic** - Data validation and settings management

Slow and steady wins the race.

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
```

If using Linux is probably that you have to add ```uv``` to your path, we can add the follow line to the shell config (like ```~/.bashr```).

```
export PATH="$HOME/.cargo/bin:$PATH"
```

Update your development workflow sections:

## Development

### Setup
```bash
# Clone the repository
git clone https://github.com/jorgemunozl/Synthetic-Data.git
cd Synthetic-Data
```

## Install dependencies

Use
```bash
uv sync
```

### Activate the virtual environment (if needed)

```bash
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

Add Ids
memory to the llm
Detect flag true false ifexist checkpoint.sqlite trivial
# Synthetic Flowchart Generator

A FastAPI service that orchestrates a LangGraph workflow to generate Mermaid flowcharts with the help of OpenAI models. The app plans, scores, and iterates on each flowchart, exports the final diagrams as both Mermaid source and PNG images, and bundles the results in a downloadable zip file.

## Key Features
- Multi-node LangGraph pipeline that plans, generates, critiques, and routes flowchart creation (`src/nodes.py`).
- FastAPI endpoints for health checks and a `/download-zip` endpoint that returns Mermaid and PNG assets.
- Automated diagram rendering that posts Mermaid definitions to the Kroki API and stores the images locally.
- Configurable topics, difficulty steps, and LLM models through `src/constants.py` and `src/config.py`.

## How It Works
1. **Planner**: creates detailed instructions for a flowchart topic at a given difficulty.
2. **Evaluation Sheet**: derives scoring criteria for the requested flow.
3. **Generator**: produces Mermaid syntax from the planner guidance.
4. **Reflector**: scores the diagram and feeds revisions back into the loop when it misses the quality bar.
5. **Router**: cycles through topics and difficulty tiers until enough diagrams are produced.
6. **Image Export**: writes Markdown and Mermaid files, renders them to PNG via Kroki, and returns the file list to the API layer.

The orchestration graph is defined in `src/main.py`, while the shared state object lives in `src/state.py`.

## Requirements
- Python 3.12+
- An OpenAI API key with access to the configured models (`gpt-4o`, `o4-mini` by default)
- `curl` available on the machine (used to call the Kroki rendering service)
- Recommended: [uv](https://github.com/astral-sh/uv) for dependency management

## Quick Start
```bash
# Clone the repository
git clone https://github.com/jorgemunozl/Synthetic-Data.git
cd Synthetic-Data

# Install uv (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Ensure output directories exist
mkdir -p flowcharts Mermaids images
```

Create a `.env` file (or export variables in your shell) with at least:
```
OPENAI_API_KEY=sk-...
```

## Running the API
```bash
uv run uvicorn src.main:app --reload
```

Once the server is running on `http://localhost:8000`, you can:
- `GET /healthcheck` – confirm the service is ready.
- `POST /download-zip` – trigger flowchart generation. The request body expects:
  ```json
  {
    "prompt": ["write documentation", "publish release notes"],
    "difficulty": 1
  }
  ```
  The current workflow ignores the free-form prompt list and instead iterates through the topics and difficulty tiers configured in `src/constants.py`. The response streams a `generated_files.zip` attachment containing:
  - `images/*.png` – rendered diagrams.
  - `mermaid/*.mmd` – raw Mermaid sources.

Example request:
```bash
curl -X POST "http://localhost:8000/download-zip" \
  -H "Content-Type: application/json" \
  -d '{"prompt":["prepare mise en place"],"difficulty":1}' \
  --output generated_files.zip
```

## Customization
- **Topics & Difficulty**: adjust `topics`, `dif`, and export directories in `src/constants.py`.
- **Model configuration**: tweak `GraphConfig` defaults (model names, temperature, recursion limits) in `src/config.py`.
- **Prompts**: update the language used by each LangChain node in `src/prompts.py`.
- **Asset folders**: the service writes to `flowcharts/`, `Mermaids/`, and `images/`. Modify the paths in `src/constants.py` if you want to point elsewhere.

## Docker (optional)
The repository includes a `Dockerfile` and `docker-compose.yml`. To build and run the service:
```bash
docker compose up --build
```
If you run the image manually, make sure the command points at the FastAPI app module:
```bash
docker build -t synthetic-flowcharts .
docker run --rm -p 8000:8000 --env-file .env synthetic-flowcharts \
  uv run -- uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Development Tips
- Use `uv run pytest` (or the Makefile targets) after you add tests.
- Kroki calls require outbound network access; if you are working offline you can skip the image step by mocking `convert_mmd_to_png`.
- The workflow stores intermediate text in `flowcharts/` and `Mermaids/`. Clean them out as needed during development.

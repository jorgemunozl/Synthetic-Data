FROM python:3.12-slim

WORKDIR /app

# Install curl (for uv installer) and any build deps; clean up apt cache.
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv CLI, pin version
RUN curl -LsSf https://astral.sh/uv/0.8.17/install.sh | sh
# Make uv available on PATH for all subsequent layers and at runtime
ENV PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"

# Copy dependency spec files early (so dependency layer can be cached)
COPY pyproject.toml uv.lock /app/

# Sync dependencies using uv with lockfile
RUN uv sync --locked

# Copy rest of code
COPY . /app

EXPOSE 8000

# Run the app via uv
CMD ["uv", "run", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

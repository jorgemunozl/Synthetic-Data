FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/0.8.17/install.sh | sh
ENV PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"

COPY pyproject.toml uv.lock /app/

RUN uv sync --locked

COPY . /app

EXPOSE 8000

CMD ["uv", "run", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

CONTAINER_NAME=growth-learnings-mcp-ai-core-container
IMAGE_NAME=growth-learnings-mcp-ai-core-IMAGE_NAME

.PHONY: all format lint test tests test_watch integration_tests docker_tests help extended_tests build-dev build-prod run-dev run-prod shell-dev shell-prod up-dev up-prod down clean logs health init-submodules verify-submodules

# Default target executed when no arguments are given to make.
all: help

# Define a variable for the test file path.
TEST_FILE ?= tests/unit_tests/

test:
	python -m pytest $(TEST_FILE)

test_watch:
	python -m ptw --snapshot-update --now . -- -vv tests/unit_tests

test_profile:
	python -m pytest -vv tests/unit_tests/ --profile-svg

extended_tests:
	python -m pytest --only-extended $(TEST_FILE)

# LINTING AND FORMATTING
# Define a variable for Python and notebook files.
PYTHON_FILES=src/
MYPY_CACHE=.mypy_cache
lint format: PYTHON_FILES=.
lint_diff format_diff: PYTHON_FILES=$(shell git diff --name-only --diff-filter=d main | grep -E '\.py$$|\.ipynb$$')
lint_package: PYTHON_FILES=src
lint_tests: PYTHON_FILES=tests
lint_tests: MYPY_CACHE=.mypy_cache_test

lint lint_diff lint_package lint_tests:
	python -m ruff check .
	[ "$(PYTHON_FILES)" = "" ] || python -m ruff format $(PYTHON_FILES) --diff
	[ "$(PYTHON_FILES)" = "" ] || python -m ruff check --select I $(PYTHON_FILES)
	[ "$(PYTHON_FILES)" = "" ] || python -m mypy --strict $(PYTHON_FILES)
	[ "$(PYTHON_FILES)" = "" ] || mkdir -p $(MYPY_CACHE) && python -m mypy --strict $(PYTHON_FILES) --cache-dir $(MYPY_CACHE)

format format_diff:
	ruff format $(PYTHON_FILES)
	ruff check --select I --fix $(PYTHON_FILES)


# DOCKER COMMANDS

# Build commands for new Dockerfile
build:
	@echo "Building development Docker image..."
	docker build --target development -t $(IMAGE_NAME_DEV) -f Dockerfile .

# Run commands for new Dockerfile
run:
	@echo "Running development container..."
	docker run -d --name $(CONTAINER_NAME_DEV) \
		-p 8001:8001 \
		-e PYTHONPATH=/app/src \
		-e ENVIRONMENT=development \
		--env-file apps/ai-core/.env \
		$(IMAGE_NAME_DEV)

# Docker Compose commands for new setup
up:
	@echo "Starting development environment with docker-compose..."
	docker-compose up -d

down:
	@echo "Stopping all containers..."
	docker-compose down

down-volumes:
	@echo "Stopping all containers and removing volumes..."
	docker-compose down -v

logs:
	@echo "Showing development logs..."
	docker-compose logs -f

# Shell commands
shell:
	@echo "Opening shell in development container..."
	docker exec -it $(CONTAINER_NAME) /bin/bash

health:
	@echo "Checking application health..."
	@curl -f http://localhost:8001/api/healthcheck || echo "Application not responding"

# CLEANING
.PHONY: clean-pycache
clean-pycache:	
	@echo ":broom: Cleaning Python cache files..."
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete

.PHONY: clean-test
clean-test:
	@echo ":broom: Cleaning test artifacts..."
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/

.PHONY: clean-container
clean-container: down
	@echo ":wastebasket:  Removing the Docker container and image..."
	@docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	@docker rmi $(IMAGE_NAME) 2>/dev/null || true

.PHONY: docker-clean
docker-clean:
	@echo ":broom: Removing unused Docker resources..."
	docker system prune -f

.PHONY: clean-all
clean-all: clean-pycache clean-test docker-clean clean-container
	@echo ":sparkles: All temporary files and caches cleaned."

# Logging Commands
.PHONY: docker-logs
docker-logs:
	@echo ":clipboard: Showing logs for all services..."
	cd apps/ai-core && docker-compose logs -f

# Development Commands
.PHONY: dev
dev: up logs
	@echo ":rocket: Development containers are running on port 8001."

# HELP
help:
	@echo ''
	@echo ':rocket: Makefile Commands'
	@echo '=================================================='
	@echo ''
	@echo ':sparkles: LINTING AND FORMATTING'
	@echo '   format                       - Run code formatters'
	@echo '   lint                         - Run linters'
	@echo '   clean-pycache                - Clean Python cache files'
	@echo '   clean-test                   - Clean test artifacts'
	@echo '   clean-all                    - Clean all temporary files and caches'
	@echo ''
	@echo ':test_tube: TESTING'
	@echo '   test                         - Run unit tests'
	@echo '   tests                        - Run unit tests'
	@echo '   test TEST_FILE=<test_file>   - Run all tests in file'
	@echo '   test_watch                   - Run unit tests in watch mode'
	@echo ''
	@echo ':whale: DOCKER COMMANDS'
	@echo '   build                     - Build development Docker image (includes submodules)'
	@echo '   run                       - Run development container with reload'
	@echo '   up                        - Start development with docker-compose'
	@echo '   down                          - Stop all containers'
	@echo '   shell                     - Open shell in development container'
	@echo '   health                        - Check application health'
	@echo '   clean-container               - Remove the Docker container'
	@echo '   docker-clean                  - Remove unused Docker resources'
	@echo '   docker-logs                   - Show logs for all services'
	@echo ''
	@echo ':hammer_and_wrench:  DEVELOPMENT'
	@echo '   dev                           - Start development environment with docker-compose (no build)'
	@echo ''
	@echo ':rocket: PRODUCTION'
	@echo '   prod                          - Build and start production container directly'
	@echo ''
	@echo ':bulb: Quick Start:'
	@echo '   make dev                      # Start development environment'
	@echo '   make test                     # Run tests'
	@echo '   make format                   # Format code'
	@echo '   make lint                     # Lint code'
	@echo ''
	@echo ':chart_with_upwards_trend: LOGGING'
	@echo '   logs                      - Show development logs'
	@echo ''
	@echo ':books: For more information, check the README.md file'
	@echo ''
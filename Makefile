#!make
PORT = 8080
SERVICE_NAME = meditherakis_service
CONTAINER_NAME = $(SERVICE_NAME)
DOCKER_COMPOSE_TAG = $(SERVICE_NAME)_1
APP_PYFILES=app/*.py
TESTS_PYFILES=tests/*/*.py
PYFILES = $(APP_PYFILES)
PYTHON_VERSION=3.12

# Virtual env
venv:
	@echo "\n🐍 Creating virtual environment..."
	python -m venv .venv

activate-venv:
	source .venv/bin/activate

# Install
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements_dev.txt

# Runs the static code analysis tools
.PHONY: lint
lint:
	@ruff check --fix ${PYFILES}
	@mypy --config-file pyproject.toml ${PYFILES}

# Formats the code using black and isort
.PHONY: format
format:
	@find ${PYFILES} -name "*.py" ! -name "test_*.py" -exec docformatter -i {} +
	@ruff format ${PYFILES}

# Checks if the code is formatted correctly
.PHONY: check
check:
	@find ${PYFILES} -name "*.py" ! -name "test_*.py" -exec docformatter -c {} +
	@ruff format --check ${PYFILES}
	@ruff check ${PYFILES}

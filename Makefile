.PHONY: help install lint format check deploy-host deploy-serial deploy-wifi clean

help:
	@echo "Pico Automation Hat - Development Commands"
	@echo ""
	@echo "  make install       - Install dependencies with uv"
	@echo "  make lint          - Run ruff linter"
	@echo "  make format        - Format code with ruff"
	@echo "  make check         - Run lint and format check"
	@echo "  make deploy-host   - Deploy host service to Raspberry Pi"
	@echo "  make deploy-serial - Deploy serial firmware to board"
	@echo "  make deploy-wifi   - Deploy WiFi firmware to board"
	@echo "  make clean         - Clean build artifacts"

install:
	@echo "Installing dependencies with uv..."
	uv pip install -e ".[dev]"

lint:
	@echo "Running ruff linter..."
	ruff check host/*.py

format:
	@echo "Formatting code with ruff..."
	ruff format host/*.py

check: lint
	@echo "Running format check..."
	ruff format --check host/*.py

deploy-host:
	@echo "Deploying host service..."
	cd host && ./deploy.sh

deploy-serial:
	@echo "Deploying serial firmware..."
	cd firmware-serial && ./deploy.sh

deploy-wifi:
	@echo "Deploying WiFi firmware..."
	cd firmware-wifi && ./deploy.sh

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

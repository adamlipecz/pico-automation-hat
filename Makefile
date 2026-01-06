.PHONY: help install lint format check deploy-host deploy-gateway deploy-serial deploy-wifi clean

help:
	@echo "Pico Automation Hat - Development Commands"
	@echo ""
	@echo "  make install       - Install dependencies with uv"
	@echo "  make lint          - Run ruff linter"
	@echo "  make format        - Format code with ruff"
	@echo "  make check         - Run lint and format check"
	@echo "  make deploy-gateway - Deploy automation gateway service to Raspberry Pi"
	@echo "  make deploy-host   - Alias for deploy-gateway (legacy name)"
	@echo "  make deploy-serial - Deploy serial firmware to board"
	@echo "  make deploy-wifi   - Deploy WiFi firmware to board"
	@echo "  make clean         - Clean build artifacts"

install:
	@echo "Installing dependencies with uv..."
	uv pip install -e ".[dev]"

lint:
	@echo "Running ruff linter..."
	ruff check automation-gateway/*.py

format:
	@echo "Formatting code with ruff..."
	ruff format automation-gateway/*.py

check: lint
	@echo "Running format check..."
	ruff format --check automation-gateway/*.py

deploy-host: deploy-gateway

deploy-gateway:
	@echo "Deploying automation gateway service..."
	cd automation-gateway && ./deploy.sh

deploy-serial:
	@echo "Deploying serial firmware..."
	cd automation-firmware-serial && ./deploy.sh

deploy-wifi:
	@echo "Deploying WiFi firmware..."
	cd automation-firmware-wifi && ./deploy.sh

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Makefile for Xenocrates development tasks
# Usage: make <target>

.PHONY: help install install-dev test lint format check clean

# Default target - show help
help:
	@echo "Xenocrates Development Commands"
	@echo "================================"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests with pytest"
	@echo "  make test-verbose  - Run tests with verbose output"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Check code with flake8"
	@echo "  make format        - Format code with black and isort"
	@echo "  make check         - Run all checks (lint + format check)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove temporary files and caches"
	@echo ""
	@echo "Quick Start:"
	@echo "  make install-dev && make test && make check"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run tests
test:
	pytest tests/ -v

# Run tests with verbose output
test-verbose:
	pytest tests/ -vv

# Run tests with coverage report
test-coverage:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Lint code with flake8
lint:
	@echo "Running flake8..."
	flake8 xenocrates.py tests/

# Format code with black and isort
format:
	@echo "Running black..."
	black xenocrates.py tests/
	@echo "Running isort..."
	isort xenocrates.py tests/

# Check formatting without making changes
format-check:
	@echo "Checking black formatting..."
	black --check xenocrates.py tests/
	@echo "Checking isort formatting..."
	isort --check xenocrates.py tests/

# Run all quality checks
check: lint format-check
	@echo ""
	@echo "✅ All checks passed!"

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov .coverage
	@echo "✅ Cleanup complete!"

# Run a quick development check (format + test + lint)
dev-check: format test lint
	@echo ""
	@echo "✅ Development check complete!"

# Show versions of tools
versions:
	@echo "Tool Versions:"
	@echo "=============="
	@python --version
	@echo -n "pytest: " && pytest --version | head -1
	@echo -n "black: " && black --version
	@echo -n "flake8: " && flake8 --version
	@echo -n "isort: " && isort --version

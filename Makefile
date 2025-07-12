.PHONY: help install install-dev clean lint format type-check test test-cov build docs

help:
	@echo "Available commands:"
	@echo "  install      Install the package in production mode"
	@echo "  install-dev  Install the package in development mode with all extras"
	@echo "  clean        Remove build artifacts and cache files"
	@echo "  lint         Run ruff linter"
	@echo "  format       Format code with black and ruff"
	@echo "  type-check   Run mypy type checker"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  build        Build distribution packages"
	@echo "  docs         Build documentation"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs]"
	pre-commit install

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/
	ruff format src/ tests/

type-check:
	mypy src/

test:
	pytest tests/

test-cov:
	pytest --cov=ai_ml_crawler --cov-report=html --cov-report=term tests/

build:
	python -m build

docs:
	cd docs && make html

pre-commit:
	pre-commit run --all-files

.PHONY: help install test lint format check clean

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run all tests"
	@echo "  make test-unit   - Run unit tests only"
	@echo "  make test-int    - Run integration tests only"
	@echo "  make test-cov    - Run tests with coverage"
	@echo "  make lint        - Run all linters"
	@echo "  make format      - Format code with black and isort"
	@echo "  make check       - Check code without formatting"
	@echo "  make pre-commit  - Install pre-commit hooks"
	@echo "  make clean       - Clean cache files"

install:
	poetry install

test:
	poetry run pytest

test-unit:
	poetry run pytest tests/unit -v

test-int:
	poetry run pytest tests/integration -v

test-cov:
	poetry run pytest --cov=app --cov-report=html --cov-report=term

lint:
	poetry run ruff check app tests
	poetry run black --check app tests
	poetry run isort --check-only app tests
	poetry run mypy app

format:
	poetry run black app tests
	poetry run isort app tests
	poetry run ruff check --fix app tests

check: lint test

pre-commit:
	poetry run pre-commit install

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov
	rm -rf .coverage

# Development task automation
.PHONY: help install test lint format clean dev

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install llms package in development mode using Poetry
	cd packages/llms && poetry install

test: ## Run tests
	poetry run pytest apps/assistant-api/tests/

lint: ## Run linting
	poetry run ruff check apps/assistant-api/
	poetry run mypy apps/assistant-api/app/

format: ## Format code
	poetry run black apps/assistant-api/
	poetry run ruff --fix apps/assistant-api/

clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

dev: install ## Start development server
	poetry run uvicorn apps/assistant-api/app.main:app --reload --host 0.0.0.0 --port 8000

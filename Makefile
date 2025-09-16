# Development task automation
.PHONY: help install test lint format clean dev docker-dev docker-prod

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

test: ## Run tests
	poetry run pytest tests/

lint: ## Run linting
	poetry run ruff check .
	poetry run mypy app/ llm/ rag/ agents/ connectors/ core/

format: ## Format code
	poetry run black .
	poetry run ruff --fix .

clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

dev: install ## Start development server
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-dev: ## Run with Docker Compose
	docker-compose up --build

docker-prod: ## Build production Docker image
	docker build -t personal-ai .
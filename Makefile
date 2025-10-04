# Development task automation
.PHONY: help install test test-api test-ai test-rag test-tuning test-quick lint format clean dev docker-dev docker-prod

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

test: ## Run all tests
	poetry run pytest tests/ -v

test-api: ## Run API tests only
	poetry run pytest tests/tests_api/ -v

test-ai: ## Run AI provider tests only
	poetry run pytest tests/tests_ai_providers/ -v

test-rag: ## Run RAG tests only
	poetry run pytest tests/tests_rag/ -v

test-tuning: ## Run tuning tests only
	poetry run pytest tests/tests_tuning/ -v

test-quick: ## Run tests with custom runner
	python tests/run_tests.py

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
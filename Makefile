.PHONY: help install install-python install-node test test-python test-js lint format clean run-notebook

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: install-python install-node ## Install all dependencies

install-python: ## Install Python dependencies
	python -m pip install --upgrade pip
	pip install -r requirements.txt

install-node: ## Install Node.js dependencies
	npm install

test: test-python test-js ## Run all tests

test-python: ## Run Python tests
	pytest tests/python/ -v

test-js: ## Run JavaScript tests
	npm test

lint: lint-python lint-js ## Run all linters

lint-python: ## Run Python linters
	black --check src/python/
	flake8 src/python/
	mypy src/python/
	pylint src/python/

lint-js: ## Run JavaScript linters
	npm run lint

format: format-python format-js ## Format all code

format-python: ## Format Python code
	black src/python/ tests/python/
	isort src/python/ tests/python/

format-js: ## Format JavaScript code
	npm run format

clean: ## Clean temporary files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ coverage/ htmlcov/ .coverage
	rm -rf node_modules/ .nyc_output/

run-notebook: ## Start Jupyter notebook server
	jupyter notebook notebooks/

build: ## Build the project
	npm run build

setup-env: ## Setup environment from .env.example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please update .env with your actual values"; \
	else \
		echo ".env file already exists"; \
	fi

check-env: ## Check if environment is properly configured
	@echo "Checking Python..."
	@python --version
	@echo "Checking Node.js..."
	@node --version
	@echo "Checking npm..."
	@npm --version
	@echo "Checking git..."
	@git --version
	@echo ""
	@echo "Environment check complete!"
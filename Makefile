.PHONY: help install dev-install test lint format type-check docker-up docker-down clean evals

help:
	@echo "AidOps AI - Available Commands"
	@echo "================================"
	@echo "install          - Install production dependencies"
	@echo "dev-install      - Install development dependencies"
	@echo "test             - Run all tests"
	@echo "lint             - Run linters (ruff, eslint)"
	@echo "format           - Format code (black, prettier)"
	@echo "type-check       - Run type checkers (mypy, tsc)"
	@echo "docker-up        - Start all services with docker-compose"
	@echo "docker-down      - Stop all services"
	@echo "evals            - Run evaluation harness"
	@echo "clean            - Clean build artifacts and cache"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev-install:
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install
	pre-commit install

test:
	cd backend && pytest tests/ -v
	cd frontend && npm test

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

format:
	cd backend && black . && ruff check --fix .
	cd frontend && npm run format

type-check:
	cd backend && mypy app/
	cd frontend && npm run type-check

docker-up:
	docker-compose -f infra/docker-compose.yml up -d

docker-down:
	docker-compose -f infra/docker-compose.yml down

evals:
	cd backend && python -m evals.run_evals

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name ".next" -exec rm -rf {} +

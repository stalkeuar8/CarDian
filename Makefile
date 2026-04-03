
PYTHON = poetry run
APP_DIR = src

.PHONY: help update build down rebuild lint format check install start

help:
	@echo "  make update 
	@echo "  make build
	@echo "  make down   
	@echo "  make rebuild  
	@echo "  make format 
	@echo "  make lint  
	@echo "  make check  
	@echo "  make install

editor:
	code .

update:
	@echo "Git Pulling..."
	git pull origin main
	@echo "Docker restarting..."
	docker compose down
	docker compose up -d --build
	@echo "Update finished!"

build:
	docker compose up -d

down:
	docker compose down

rebuild:
	docker compose up -d --build

format:
	@echo "Formatting code with Ruff..."
	$(PYTHON) ruff format .
	$(PYTHON) ruff check . --fix

lint:
	@echo "Checking styles and types..."
	$(PYTHON) ruff check .
	$(PYTHON) mypy .

check: format lint
	@echo "All checks passed!"

install:
	@echo "Installing dependencies with Poetry..."
	poetry install

start: editor install check rebuild
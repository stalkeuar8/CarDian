
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


build:
	docker compose -p cardian up --build

up:
	docker compose -p cardian down
	docker compose -p cardian up 

down:
	docker compose -p cardian down

restart: up

rebuild:
	docker compose -p cardian down
	docker compose -p cardian up --build

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
	
env_activate: 
	poetry env activate

migration:
	docker compose run --rm migrations alembic revision --autogenerate -m "$(mes)"
	docker compose run --rm migrations alembic upgrade head


start: editor update install env_activate up 
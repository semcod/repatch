.PHONY: dev seed up down build test

dev: seed
	uvicorn repatch.dev_server:app --reload --host 0.0.0.0 --port 8000

seed:
	python -m repatch.seeds

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

test:
	pytest

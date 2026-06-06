VENV ?= .venv
PYTHON ?= $(shell test -x $(VENV)/bin/python && echo $(VENV)/bin/python || echo python3)
export PYTHONPATH := src
API_HOST ?= 0.0.0.0
API_PORT ?= 8080

.PHONY: install demo active test run-api docker-up docker-down docker-logs dvc-repro benchmark-generalization

install: $(VENV)/bin/python
	$(VENV)/bin/pip install -r requirements.txt

$(VENV)/bin/python:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip

demo:
	$(PYTHON) src/luthor/demo.py

active:
	$(PYTHON) src/luthor/active_demo.py

test:
	$(PYTHON) -m unittest discover -s tests -v

run-api:
	uvicorn luthor.api.main:app --host $(API_HOST) --port $(API_PORT) --reload

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api

docker-monitoring:
	docker compose up -d prometheus grafana

dvc-repro:
	dvc repro

benchmark-generalization:
	$(PYTHON) src/luthor/benchmark_generalization.py

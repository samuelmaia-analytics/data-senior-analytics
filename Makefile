SHELL := /bin/bash

.PHONY: setup install install-dev lint test quality preflight format run

setup: install-dev

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	python -m ruff check src config scripts dashboard tests
	python -m black --check src config scripts dashboard tests

test:
	python -m pytest

run:
	streamlit run dashboard/app.py

preflight:
	python scripts/check_encoding.py
	python scripts/streamlit_cloud_preflight.py
	python scripts/validate_data_provenance.py

quality: lint test preflight

format:
	python -m ruff format src config scripts dashboard tests
	python -m black src config scripts dashboard tests

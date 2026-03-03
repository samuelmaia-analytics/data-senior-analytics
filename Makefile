SHELL := /bin/bash

.PHONY: install install-dev lint test quality preflight format

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

install-dev:
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	python -m ruff check src config scripts dashboard tests

test:
	python -m pytest

preflight:
	python scripts/check_encoding.py
	python scripts/streamlit_cloud_preflight.py
	python scripts/validate_data_provenance.py

quality: lint test preflight

format:
	python -m ruff format src config scripts dashboard tests

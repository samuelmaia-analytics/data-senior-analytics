SHELL := /bin/bash

.PHONY: setup install install-dev lint test quality preflight format run manifest security purge-retention

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
	python -m black --line-length 100 --target-version py311 --check src config scripts dashboard tests

test:
	python -m pytest

run:
	streamlit run dashboard/app.py

preflight:
	python scripts/check_encoding.py
	python scripts/streamlit_cloud_preflight.py
	python scripts/validate_data_provenance.py
	python scripts/generate_data_manifest.py --check
	python scripts/check_secrets.py

quality: lint test preflight

format:
	python -m ruff format src config scripts dashboard tests
	python -m black --line-length 100 --target-version py311 src config scripts dashboard tests

manifest:
	python scripts/generate_data_manifest.py

security:
	python scripts/check_secrets.py

purge-retention:
	python scripts/purge_expired_datasets.py

SHELL := /bin/sh

PYTHON ?= python
HISTORICAL_NOTEBOOK := notebooks/tcc-reconstructed.ipynb
EVOLVED_NOTEBOOK := notebooks/tcc-evolved.ipynb
EXPORT_DIR := artifacts/html
EVOLVED_HTML_EXPORT := $(EXPORT_DIR)/tcc-evolved.html
HISTORICAL_HTML_EXPORT := $(EXPORT_DIR)/tcc-reconstructed.html

.DEFAULT_GOAL := help

.PHONY: help install test validate validate-reconstruction validate-evolved \
	validate-html validate-html-reconstructed notebook notebook-evolved \
	reproduce-reconstructed export export-evolved export-reconstructed

help:
	@echo "Available targets: install test validate validate-evolved notebook notebook-evolved reproduce-reconstructed export export-reconstructed"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -v

validate:
	$(PYTHON) scripts/verify_source_integrity.py
	$(PYTHON) scripts/validate_final_reconstruction.py
	$(PYTHON) -m scripts.validate_evolved_notebook
	$(PYTHON) -m pip check
	git diff --check

validate-reconstruction:
	$(PYTHON) scripts/verify_source_integrity.py
	$(PYTHON) scripts/validate_final_reconstruction.py

validate-evolved:
	$(PYTHON) scripts/verify_source_integrity.py
	$(PYTHON) -m scripts.validate_evolved_notebook

validate-html:
	$(PYTHON) scripts/validate_local_html.py "$(EVOLVED_HTML_EXPORT)"

validate-html-reconstructed:
	$(PYTHON) scripts/validate_local_html.py "$(HISTORICAL_HTML_EXPORT)"

notebook:
	$(MAKE) notebook-evolved PYTHON="$(PYTHON)"

notebook-evolved:
	@test -n "$$LENDING_CLUB_DATA_PATH" || { echo "LENDING_CLUB_DATA_PATH is required" >&2; exit 2; }
	@test -f "$$LENDING_CLUB_DATA_PATH" || { echo "Dataset not found: $$LENDING_CLUB_DATA_PATH" >&2; exit 2; }
	LENDING_CLUB_DATA_PATH="$$LENDING_CLUB_DATA_PATH" $(PYTHON) -m jupyter nbconvert \
		--to notebook \
		--execute \
		--inplace "$(EVOLVED_NOTEBOOK)" \
		--ExecutePreprocessor.timeout=1800

reproduce-reconstructed:
	@test -n "$$LENDING_CLUB_DATA_PATH" || { echo "LENDING_CLUB_DATA_PATH is required" >&2; exit 2; }
	@test -f "$$LENDING_CLUB_DATA_PATH" || { echo "Dataset not found: $$LENDING_CLUB_DATA_PATH" >&2; exit 2; }
	LENDING_CLUB_DATA_PATH="$$LENDING_CLUB_DATA_PATH" $(PYTHON) -m scripts.reproduce_historical_notebook

export:
	$(MAKE) export-evolved PYTHON="$(PYTHON)"

export-evolved:
	$(PYTHON) scripts/export_notebook_html.py \
		--notebook "$(EVOLVED_NOTEBOOK)" \
		--output "$(EVOLVED_HTML_EXPORT)"

export-reconstructed:
	$(PYTHON) scripts/export_notebook_html.py \
		--notebook "$(HISTORICAL_NOTEBOOK)" \
		--output "$(HISTORICAL_HTML_EXPORT)"

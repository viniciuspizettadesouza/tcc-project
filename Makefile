SHELL := /bin/sh

PYTHON ?= python
NOTEBOOK := notebooks/tcc-reconstructed.ipynb
EXPORT_DIR := artifacts/html
HTML_EXPORT := $(EXPORT_DIR)/tcc-reconstructed.html

.DEFAULT_GOAL := help

.PHONY: help install test validate validate-html notebook export

help:
	@echo "Available targets: install test validate validate-html notebook export"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -v

validate:
	$(PYTHON) scripts/verify_source_integrity.py
	$(PYTHON) scripts/validate_final_reconstruction.py
	$(PYTHON) -m pip check
	git diff --check

validate-html:
	$(PYTHON) scripts/validate_local_html.py "$(HTML_EXPORT)"

notebook:
	@test -n "$$LENDING_CLUB_DATA_PATH" || { echo "LENDING_CLUB_DATA_PATH is required" >&2; exit 2; }
	@test -f "$$LENDING_CLUB_DATA_PATH" || { echo "Dataset not found: $$LENDING_CLUB_DATA_PATH" >&2; exit 2; }
	LENDING_CLUB_DATA_PATH="$$LENDING_CLUB_DATA_PATH" $(PYTHON) -m jupyter nbconvert \
		--to notebook \
		--execute \
		--inplace "$(NOTEBOOK)" \
		--ExecutePreprocessor.timeout=1800

export:
	$(PYTHON) scripts/export_notebook_html.py \
		--notebook "$(NOTEBOOK)" \
		--output "$(HTML_EXPORT)"

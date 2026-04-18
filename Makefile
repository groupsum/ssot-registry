.PHONY: test test-core test-package lint build-package build-all release-metadata

PACKAGE ?= ssot-registry
PROJECT_PATH = pkgs/$(PACKAGE)

test: test-core

test-core:
	python -m unittest discover -s tests -v

test-package:
	uv sync --python 3.12 --package $(PACKAGE)
	uv run --python 3.12 --package $(PACKAGE) --no-sync python -m unittest discover -s tests -v

lint:
	python -m compileall pkgs tests

build-package:
	uv build --project $(PROJECT_PATH)

build-all:
	uv build --project pkgs/ssot-contracts
	uv build --project pkgs/ssot-views
	uv build --project pkgs/ssot-codegen
	uv build --project pkgs/ssot-core
	uv build --project pkgs/ssot-registry
	uv build --project pkgs/ssot-cli
	uv build --project pkgs/ssot-tui

release-metadata:
	python scripts/release_metadata.py show

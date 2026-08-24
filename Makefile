PYTHON ?= python3
TESTS  := discover -s ./tests -p '*_test.py'

.DEFAULT_GOAL := help
.PHONY: help install lint format typecheck test coverage check build clean

help: ## Show the available targets
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in editable mode with the dev extras
	$(PYTHON) -m pip install -e '.[dev]'

lint: ## Check style and formatting
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

format: ## Apply formatting and safe autofixes
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check --fix .

typecheck: ## Run mypy in strict mode
	$(PYTHON) -m mypy

test: ## Run the test suite
	$(PYTHON) -m unittest $(TESTS)

coverage: ## Run the suite under coverage and enforce the threshold
	$(PYTHON) -m coverage run -m unittest $(TESTS)
	$(PYTHON) -m coverage report

check: lint typecheck coverage ## Everything CI runs

build: clean ## Build the sdist and wheel, then validate them
	$(PYTHON) -m build
	$(PYTHON) -m twine check --strict dist/*

clean: ## Remove build and tool artefacts
	rm -rf build dist ./*.egg-info .coverage .mypy_cache .ruff_cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +

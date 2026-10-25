# One entry point for the checks CI runs. `make check` before every push.
PYTHON := .venv/bin/python

.PHONY: venv test lint diagram check

venv: ## Test environment with the locked dependencies, ruff and pytest
	python3 -m venv .venv
	.venv/bin/pip install -q --require-hashes -r requirements.lock.txt
	.venv/bin/pip install -q pytest ruff

test: ## The pytest suite (Slack is mocked)
	$(PYTHON) -m pytest -q tests

lint: ## ruff
	$(PYTHON) -m ruff check src tests

diagram: ## Redraw docs/assets/*.svg
	python3 tools/gen_diagram.py

check: lint test ## Everything CI checks
	python3 tools/gen_diagram.py --check

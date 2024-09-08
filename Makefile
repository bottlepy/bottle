VERSION = $(shell ./bottle.py --version)
VENV = build/venv

.PHONY: test
test: venv
	$(VENV)/bin/pytest

.PHONY: coverage
coverage: venv
	$(VENV)/bin/pytest -q --cov=bottle --cov-report=term --cov-report=html:build/htmlcov

.PHONY: build
build: test
	$(VENV)/bin/python -m build

.PHONY: docs
docs: venv
	$(VENV)/bin/sphinx-build -b html docs build/docs/html/;

.PHONY: watchdocs
watchdocs: venv
	-mkdir -p build/docs/watch/
	$(VENV)/bin/sphinx-autobuild -b html docs build/docs/watch/;

.PHONY: version
version:
	@echo $(VERSION)

.PHONY: venv
venv: $(VENV)/.installed
$(VENV)/.installed: Makefile pyproject.toml
	test -d $(VENV) || python3 -m venv $(VENV)
	$(VENV)/bin/python3 -m ensurepip
	$(VENV)/bin/pip install -q -U pip
	$(VENV)/bin/pip install -q -e .[dev]
	touch $(VENV)/.installed

.PHONY: venv
clean:
	rm -rf $(VENV) build/ dist/ MANIFEST .coverage .pytest_cache bottle.egg-info 2>/dev/null || true
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +

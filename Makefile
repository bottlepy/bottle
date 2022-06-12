PATH := build/python/bin:$(PATH)
VERSION = $(shell python setup.py --version)
ALLFILES = $(shell echo bottle.py test/*.py test/views/*.tpl)
VENV = build/venv

.PHONY: release coverage install docs test 2to3 clean

release: clean venv
	$(VENV)/bin/python3 setup.py --version | egrep -q -v '[a-zA-Z]' # Fail on dev/rc versions
	git commit -e -m "Release of $(VERSION)"            # Fail on nothing to commit
	git tag -a -m "Release of $(VERSION)" $(VERSION)    # Fail on existing tags
	git push origin HEAD                                # Fail on out-of-sync upstream
	git push origin tag $(VERSION)                      # Fail on dublicate tag
	$(VENV)/bin/python3 setup.py sdist bdist_wheel      # Build project
	$(VENV)/bin/twine upload dist/$(VERSION)*           # Release to pypi

venv: $(VENV)/.installed
$(VENV)/.installed: Makefile
	python3 -mvenv $(VENV)
	$(VENV)/bin/python3 -mensurepip
	$(VENV)/bin/pip install -U pip
	$(VENV)/bin/pip install -U setuptools wheel twine coverage
	touch $(VENV)/.installed

coverage:
	-mkdir build/
	coverage erase
	COVERAGE_PROCESS_START=.coveragerc python -m unittest discover
	coverage combine
	coverage report
	coverage html

push: test
	git push origin HEAD

install:
	python setup.py install

docs:
	sphinx-build -b html -d build/docs/doctrees docs build/docs/html

test:
	python -m unittest discover

clean:
	rm -rf build/ dist/ MANIFEST 2>/dev/null || true
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +
	find . -name '.coverage*' -exec rm -f {} +

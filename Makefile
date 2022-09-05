VERSION = $(shell python setup.py --version)
ALLFILES = $(shell echo bottle.py test/*.py test/views/*.tpl)
VENV = build/venv
TESTBUILD = build/python

.PHONY: venv release coverage install docs test test_27 test_36 test_37 test_38 test_39 clean

release: clean test_all venv
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
	$(VENV)/bin/pip install -U setuptools wheel twine pytest coverage
	$(VENV)/bin/pip install -U sphinx sphinx-intl transifex-client
	touch $(VENV)/.installed

coverage: venv
	$(VENV)/bin/coverage erase
	$(VENV)/bin/coverage run -m pytest
	$(VENV)/bin/coverage combine
	$(VENV)/bin/coverage report
	$(VENV)/bin/coverage html

push: test_all
	git push origin HEAD

install:
	python setup.py install

docs: venv
	$(VENV)/bin/sphinx-build -b html -d build/docs/doctrees docs build/docs/html/;

tx-pull: venv
	. $(VENV)/bin/activate; \
	cd docs/_locale/ \
	&& tx pull -af

tx-push: venv
	. $(VENV)/bin/activate; \
	cd docs/_locale/ \
	&& sphinx-build -b gettext -E .. _pot \
	&& sphinx-intl update-txconfig-resources -p _pot -d . --transifex-project-name bottle \
	&& tx push -s

tx:
	$(MAKE) tx-push
	$(MAKE) tx-pull

test: venv
	. $(VENV)/bin/activate; pytest

clean:
	rm -rf $(VENV) build/ dist/ MANIFEST .coverage .name htmlcov  2>/dev/null || true
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +

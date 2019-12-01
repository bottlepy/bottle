VERSION = $(shell python setup.py --version)
ALLFILES = $(shell echo bottle.py test/*.py test/views/*.tpl)
VENV = build/venv
TESTBUILD = build/python

.PHONY: venv release coverage install docs test test_all test_27 test_32 test_33 test_34 test_35 2to3 clean

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
	$(VENV)/bin/pip install -U setuptools wheel twine coverage
	touch $(VENV)/.installed

coverage: venv
	$(VENV)/bin/coverage erase
	$(VENV)/bin/coverage run -m unittest discover
	$(VENV)/bin/coverage combine
	$(VENV)/bin/coverage report
	$(VENV)/bin/coverage html

push: test_all
	git push origin HEAD

install:
	python setup.py install

docs:
	sphinx-build -b html -d build/docs/doctrees docs build/docs/html/;

test: venv
	$(VENV)/bin/python3 -m unittest discover

test_all: test_27 test_32 test_33 test_34 test_35 test_37

test_27:
	$(TESTBUILD)/bin/python2.7 -m unittest discover

test_34:
	$(TESTBUILD)/bin/python3.4 -m unittest discover

test_35:
	$(TESTBUILD)/bin/python3.5 -m unittest discover

test_36:
	$(TESTBUILD)/bin/python3.6 -m unittest discover

test_37:
	$(TESTBUILD)/bin/python3.7 -m unittest discover

test_setup:
	bash test/build_python.sh 2.7.3 $(TESTBUILD)
	bash test/build_python.sh 3.4.9 $(TESTBUILD)
	bash test/build_python.sh 3.5.6 $(TESTBUILD)
	bash test/build_python.sh 3.6.7 $(TESTBUILD)
	bash test/build_python.sh 3.7.1 $(TESTBUILD)

clean:
	rm -rf $(VENV) build/ dist/ MANIFEST .coverage .name htmlcov  2>/dev/null || true
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +

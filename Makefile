PATH := build/python/bin:$(PATH)
VERSION = $(shell python setup.py --version)
ALLFILES = $(shell echo bottle.py test/*.py test/views/*.tpl)

.PHONY: release coverage install docs test test_all test_27 test_32 test_33 test_34 test_35 2to3 clean

release: test_all
	python setup.py --version | egrep -q -v '[a-zA-Z]' # Fail on dev/rc versions
	git commit -e -m "Release of $(VERSION)"           # Fail on nothing to commit
	git tag -a -m "Release of $(VERSION)" $(VERSION)   # Fail on existing tags
	git push origin HEAD                               # Fail on out-of-sync upstream
	git push origin tag $(VERSION)                     # Fail on dublicate tag
	python setup.py sdist bdist_wheel register upload  # Release to pypi

coverage:
	python -m coverage erase
	python -m coverage run --source=bottle.py test/testall.py
	python -m coverage combine
	python -m coverage report
	python -m coverage html

push: test_all
	git push origin HEAD

install:
	python setup.py install

docs:
	sphinx-build -b html -d build/docs/doctrees docs build/docs/html/;

test:
	python test/testall.py

test_all: test_27 test_32 test_33 test_34 test_35

test_27:
	python2.7 test/testall.py

test_32:
	python3.2 test/testall.py

test_33:
	python3.3 test/testall.py

test_34:
	python3.4 test/testall.py

test_35:
	python3.5 test/testall.py

test_setup:
	bash test/build_python.sh 2.7 build/python
	bash test/build_python.sh 3.2 build/python
	bash test/build_python.sh 3.3 build/python
	bash test/build_python.sh 3.4 build/python
	bash test/build_python.sh 3.5 build/python

clean:
	rm -rf build/ dist/ MANIFEST 2>/dev/null || true
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +


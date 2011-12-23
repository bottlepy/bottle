PATH := build/python/bin:$(PATH)
VERSION = $(shell python setup.py --version)
ALLFILES = $(shell echo bottle.py test/*.py test/views/*.tpl)

.PHONY: release install docs test test_all test_25 test_26 test_27 test_31 test_32 2to3 clean

release: test_all
	python setup.py --version | egrep -q -v '[a-zA-Z]' # Fail on dev/rc versions
	git commit -e -m "Release of $(VERSION)"           # Fail on nothing to commit
	git tag -a -m "Release of $(VERSION)" $(VERSION)   # Fail on existing tags
	python setup.py sdist register upload              # Release to pypi
	echo "Do not forget to: git push --tags"

install:
	python setup.py install

docs:
	cd docs/; $(MAKE) html

test:
	python test/testall.py

test_all: test_25 test_26 test_27 test_31 test_32

test_25:
	python2.5 test/testall.py

test_26:
	python2.6 test/testall.py

test_27:
	python2.7 test/testall.py

test_31:
	python3.1 test/testall.py

test_32:
	python3.2 test/testall.py

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +
	find . -name '.coverage*' -exec rm -f {} +
	rm -rf build/ dist/ MANIFEST 2>/dev/null || true


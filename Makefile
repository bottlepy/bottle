PATH := build/python/bin:$(PATH)
VERSION = $(shell python setup.py --version)
ALLFILES = $(shell echo bottle.py test/*.py test/views/*.tpl)

.PHONY: release install docs test test_all test_25 test_26 test_27 test_31 test_32 2to3 clean

release: test
	python setup.py --version | egrep -q -v '[a-zA-Z]' # Fail on dev/rc versions
	git tag -a -m "Release of $(VERSION)" $(VERSION) # Fail on existing tags
	python setup.py sdist register upload # Release to pypi
	echo "Don't forget to 'git push --tags'!"

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

test_31: 2to3
	python3.1 build/2to3/test/testall.py

test_32: 2to3
	python3.2 build/2to3/test/testall.py

# If anyne knows a better way, please tell me
# This builds missig files in build/2to3 by either copying or 2to3-ing them.

2to3: $(addprefix build/2to3/,$(ALLFILES))

build/2to3/%.tpl: %.tpl
	mkdir -p `dirname $@`
	cp -a $< $@

build/2to3/%.py: %.py
	mkdir -p `dirname $@`
	cp -a $< $@
	2to3 -w $@ 1>/dev/null

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +
	find . -name '.coverage*' -exec rm -f {} +
	rm -rf build/ dist/ MANIFEST 2>/dev/null || true


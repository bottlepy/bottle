.PHONY: test coverage html_coverage release clean


test:
	bash run_tests.sh

coverage:
	python test/testall.py coverage

html_coverage:
	python test/testall.py coverage html

release:
	python setup.py release sdist upload

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +
	find . -name '.coverage*' -exec rm -f {} +

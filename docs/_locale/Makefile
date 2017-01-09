pull: venv
	echo "Pulling new translations from transiflex..."
	. ../../build/venv/bin/activate; tx pull -af

push: venv
	echo "Pushing new documentation to transiflex..."
	. ../../build/venv/bin/activate; \
	sphinx-build -b gettext -E .. _pot && \
	sphinx-intl update-txconfig-resources -p _pot -d . --transifex-project-name bottle
	# Reset all *.pot files that differ only in one line (the creation date).
	for pot in `find _pot -name '*.pot'`; do\
	  git diff --numstat -- $$pot | sed 's/\t/ /g' | grep -q '1 1 docs'\
	  && echo "Not changed: $$pot" && git checkout -- $$pot || true;\
	done;
	. ../../build/venv/bin/activate; tx push -s

venv: ../../build/venv/bin/activate
../../build/venv/bin/activate: requirements.txt
	test -d ../../build/venv || python2 -mvirtualenv ../../build/venv
	../../build/venv/bin/pip install -Ur requirements.txt
	touch ../../build/venv/bin/activate

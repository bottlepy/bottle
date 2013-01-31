======================
Requirements and Setup
======================

You need python-sphinx (pip install sphinx) and gettext (for msgmerge and msgfmt).
A translation file editor (e.g. poedit) helps a lot.

Translation Workflow
====================

Run docs/_locale/update.sh before and after editing *.po files to merge new
sentences and check for errors.

Do not add *.mo files to the repository, even if your editor creates them.
We only need the *.po files.

Add a new language
==================

Add your language (two-letter code) to 'update.sh' and run it. A new
two-letter directory will appear with all the *.po files in it.

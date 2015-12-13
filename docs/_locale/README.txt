Translation Workflow
====================

  * Install dependencies (`pip install sphinx sphinx-intl`)

  * Run `bash update.sh xx_XX` with your language code. (e.g. en_US)

  * Edit the `*.po` files in the `xx_XX/LC_MESSAGES/` folder but not from
    the `_pot` subfolder. A translation file editor (e.g. poedit) helps a
    lot.

  * Run `bash update.sh xx_XX` again to check for errors. Do not commit
    the `*.mo` files to the repository, even if your editor creates them.
    We only need the *.po files.

#!/bin/bash
cd "$( cd "$( dirname "$0" )" && pwd )"

LANGUAGES='zh_CN'

echo 'Generating new POT files ...'
sphinx-build -q -b gettext -E .. _pot

echo 'Merging and compiling *.po files ...'
for LANG in $LANGUAGES; do
  for POT in _pot/*.pot; do
    DOC=`basename $POT .pot`
    echo $LANG/$DOC.po
    test -d $LANG/LC_MESSAGES || mkdir -p $LANG/LC_MESSAGES
    test -f $LANG/$DOC.po || cp $POT $LANG/$DOC.po
    msgmerge --quiet --backup=none -U $LANG/$DOC.po $POT
    msgfmt $LANG/$DOC.po -o "$LANG/LC_MESSAGES/$DOC.mo"
  done
done

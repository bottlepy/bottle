#!/bin/bash
cd "$( cd "$( dirname "$0" )" && pwd )"

if [ ! $# -eq 1 ]; then
    LNG=$(ls -1 | egrep '[a-z]{2}_[A-Z]{2}')
elif [[ $1 =~ ^[a-z]{2}_[A-Z]{2}$ ]]; then
    LNG=$1
else
    echo "$1: Language must be of form xx_XX (e.g. en_US or de_DE)"
    exit 1
fi

echo 'Generating new POT files ...'
sphinx-build -q -b gettext -E .. _pot
for L in $LNG; do
    echo
    echo "Updating po files for $L ..."
    sphinx-intl update -p _pot -d . -l $L
done
echo
echo 'Building ...'
sphinx-intl build

echo
echo "Updating transiflex stuff. This might fail. Don't worry."
sphinx-intl update-txconfig-resources -p _pot -d . --transifex-project-name bottle
tx push -s

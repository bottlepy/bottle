#!/bin/bash

set -e
set -x

if test -n "$PY"; then
  # https://github.com/pycurl/pycurl/blob/master/tests/travis/setup.sh
  sudo add-apt-repository -y ppa:fkrull/deadsnakes
  sudo apt-get update
  sudo apt-get install python$PY-dev
fi

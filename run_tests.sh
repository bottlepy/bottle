#!/bin/bash

root=`pwd`
if [ -d "$root/tbuild/opt/bin" ]; then
    PATH="$root/tbuild/opt/bin:$PATH"
fi

function fail {
  cat test.log
  echo -e "\e[0;31mFAILED! :(\e[0m"
  exit 1
}

function runtest {
    if type $1 &>/dev/null ; then
        $1 $2/testall.py &> test.log || fail
    else
        echo "Warning: Skipping test for $1 (Not installed)"
    fi
}

runtest python2.5 test
runtest python2.6 test
runtest python2.7 test

if type 2to3 &> /dev/null ; then
    rm -rf test3k &> /dev/null
    mkdir test3k
    cp -a test/* test3k
    cp bottle.py test3k
    2to3 -w test3k/*.py &> 2to3.log || fail

    runtest python3.0 test3k
    runtest python3.1 test3k
    runtest python3.2 test3k

    rm -rf test3k
fi

echo -e "\e[0;32mPASSED :)\e[0m"


#!/bin/bash -e
# This script builds a specific python release to a prefix directory

# Stop on any errors
trap exit ERR

VERSION=$1
PREFIX=$2

test -d $PREFIX || mkdir -p $PREFIX || die "ERROR: Could not find/create $PREFIX"
PREFIX=`cd $PREFIX; pwd`

PATH="$PREFIX/bin:$PATH"

# Add ubuntus special lib and include dirs so python can find them.
export arch=$(dpkg-architecture -qDEB_HOST_MULTIARCH)
export LDFLAGS="-L/usr/lib/$arch -L/lib/$arch"
export CFLAGS="-I/usr/include/$arch"
export CPPFLAGS="-I/usr/include/$arch"

if [ -x $PREFIX/bin/python$VERSION ]; then
    echo "Found Python executable. Skipping build"
    exit 0
fi

pushd $PREFIX || exit 1
  echo "Downloading source ..."
  wget -N http://hg.python.org/cpython/archive/$VERSION.tar.gz  || exit 1

  echo "Extracting source ..."
  tar -xzf $VERSION.tar.gz || exit 1

  pushd cpython-$VERSION || exit 1
    echo "Running ./configure --prefix=$PREFIX ..."
    ./configure --prefix=$PREFIX || exit 1

    echo "Running make && make install ..."
    (make -j8 && make install) || exit 1

    echo "Installing distribute and pip..."
    hash -r

  popd

  echo "Cleaning up..."
  rm -rf $VERSION.tar.gz distribute_setup.py cpython-$VERSION
popd




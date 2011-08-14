#!/usr/bin/env bash

# PREFIX and DESTDIR could be used for package creation
prefix="${PREFIX:-/usr/local}"

# Destination directories and replacement variables
program_dest="$DESTDIR$prefix/bin"
doc_dest="$DESTDIR$prefix/share/doc/putmail"
man_dest="$DESTDIR$prefix/share/man"

# Origin directory
orig="$( dirname $0 )"

# Create directories if necessary
if [ ! -e "$program_dest" ]; then
  echo "Creating directory $program_dest ... "
  mkdir -p "$program_dest"  || exit 1
fi
if [ ! -e "$doc_dest" ]; then
  echo "Creating directory $doc_dest ... "
  mkdir -p "$doc_dest" || exit 1  
fi
if [ ! -e "$man_dest" ]; then
  echo "Creating directory $man_dest ... "
  mkdir -p "$man_dest" || exit 1  
fi

# Copy the files over
echo "Copying files to $program_dest ... "
cp "$orig"/putmail* $program_dest || exit 1

echo "Copying files to $doc_dest ... "
cp "$orig"/doc/* "$doc_dest" || exit 1  

echo "Copying files to $man_dest ... "
cp -R "$orig"/man/* "$man_dest" || exit 1  

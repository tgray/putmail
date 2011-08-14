#!/usr/bin/env bash

# PREFIX and DESTDIR could be used for package creation
prefix="${PREFIX:-/usr/local}"

# Destination directories and replacement variables
program_dest="$DESTDIR$prefix/bin"
doc_dest="$DESTDIR$prefix/share/doc/putmail"
man_dest="$DESTDIR$prefix/share/man"
i18n_dest="$DESTDIR$prefix/share/locale"

# Origin directory
orig="$( dirname $0 )"

# Create directories if necessary
if [ ! -e "$program_dest" ]; then
  echo -n "Creating directory ${program_dest}... "
  { mkdir -p "$program_dest" &>/dev/null && echo "done." ; } ||
  { echo "failed." && exit 1 ; }
fi
if [ ! -e "$doc_dest" ]; then
  echo -n "Creating directory ${doc_dest}... "
  { mkdir -p "$doc_dest" &>/dev/null && echo "done." ; } ||
  { echo "failed." && exit 1 ; }
fi
if [ ! -e "$man_dest" ]; then
  echo -n "Creating directory ${man_dest}... "
  { mkdir -p "$man_dest" &>/dev/null && echo "done." ; } ||
  { echo "failed." && exit 1 ; }
fi
if [ ! -e "$i18n_dest" ]; then
  echo -n "Creating directory ${i18n_dest}... "
  { mkdir -p "$i18n_dest" &>/dev/null && echo "done." ; } ||
  { echo "failed." && exit 1 ; }
fi

# Copy the files over
echo -n "Copying files to $program_dest ... "
{ cp "$orig"/putmail*.py "$program_dest" &>/dev/null && echo "done." ; } ||
{ echo "failed." && exit 1 ; }

echo -n "Copying files to ${doc_dest}... "
{ cp "$orig"/doc/* "$doc_dest" &>/dev/null && echo "done." ; } ||
{ echo "failed." && exit 1 ; }

echo -n "Copying files to ${man_dest}... "
{ cp -R "$orig"/man/* "$man_dest" &>/dev/null && echo "done." ; } ||
{ echo "failed." && exit 1 ; }

echo -n "Copying files to ${i18n_dest}... "
{ cp -R "$orig"/i18n/* "$i18n_dest" &>/dev/null && echo "done." ; } ||
{ echo "failed." && exit 1 ; }

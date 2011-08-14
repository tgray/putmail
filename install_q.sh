#!/usr/bin/env bash

program_dest=/usr/local/bin
i18n_dest=/usr/share/locale
doc_dest=/usr/local/share/doc/putmail-queue
man_dest=/usr/local/share/man

# Create directories if necessary
if [ ! -e "$program_dest" ]; then
  echo -n "Creating directory ${program_dest}... "
  { mkdir -p "$program_dest" &>/dev/null && echo "done." ; } ||
  { echo "failed." && exit 1 ; }
fi
if [ ! -e "$i18n_dest" ]; then
  echo -n "Creating directory ${i18n_dest}... "
  { mkdir -p "$i18n_dest" &>/dev/null && echo "done." ; } ||
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

# Copy the files over
echo -n "Copying files to ${program_dest}... "
{ cp putmail*.py "$program_dest" &>/dev/null && echo "done." ; } ||
{ echo "failed." && exit 1 ; }

echo -n "Copying files to ${i18n_dest}... "
{ cp -R i18n/* "$i18n_dest" &>/dev/null && echo "done." ; } ||
{ echo "failed." && exit 1 ; }

echo -n "Copying files to ${doc_dest}... "
{ cp doc/* "$doc_dest" &>/dev/null && echo "done." ; } ||
{ echo "failed." && exit 1 ; }

echo -n "Copying files to ${man_dest}... "
{ cp -R man/* "$man_dest" &>/dev/null && echo "done." ; } ||
{ echo "failed." && exit 1 ; }

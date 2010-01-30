#!/usr/bin/env bash

# To uninstall properly, you should use the same PREFIX and DESTDIR
# used when installing.

# PREFIX and DESTDIR could be used for package creation
prefix="${PREFIX:-/usr/local}"

# Destination directories and replacement variables
program_dest="$DESTDIR$prefix/bin"
doc_dest="$DESTDIR$prefix/share/doc/putmail"
man_dest="$DESTDIR$prefix/share/man"

# Remove the files
echo "Removing $program_dest/putmail.py ... "
rm -f "$program_dest/putmail.py"

echo "Removing $doc_dest ... "
rm -fr "$doc_dest"

echo "Removing $man_dest/man1/putmail.py.1 ... "
rm -f "$man_dest/man1/putmail.py.1"

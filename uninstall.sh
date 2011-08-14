#!/usr/bin/env bash

# To uninstall properly, you should use the same PREFIX and DESTDIR
# used when installing.

# PREFIX and DESTDIR could be used for package creation
prefix="${PREFIX:-/usr/local}"

# Destination directories and replacement variables
program_dest="$DESTDIR$prefix/bin"
doc_dest="$DESTDIR$prefix/share/doc/putmail"
man_dest="$DESTDIR$prefix/share/man"
i18n_dest="$DESTDIR$prefix/share/locale"

# Remove the files
echo "Removing $program_dest/putmail.py ... "
rm -f "$program_dest/putmail.py"
rm -f "$program_dest/putmail_enqueue.py"
rm -f "$program_dest/putmail_dequeue.py"

echo "Removing $doc_dest ... "
rm -fr "$doc_dest"

echo "Removing $man_dest/man1/putmail.py.1 ... "
rm -f "$man_dest/man1/putmail.py.1"
rm -f "$man_dest/man1/putmail-queue.1"

echo "Removing $i18n_dest ... "
rm -fr "$i18n_dest/es/LC_MESSAGES/putmail_enqueue.py.mo"
rm -fr "$i18n_dest/es/LC_MESSAGES/putmail_dequeue.py.mo"

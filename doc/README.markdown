About
-----

putmail
=======

Putmail is a very lightweight MTA or SMTP client, distributed under the
terms of the X Consortium License. It is designed to replace the
sendmail command when used with MUAs that lack SMTP support, like mutt.
Its main features are:

- Command-line compatibility with sendmail.
- TLS support. SSL can also be used with an external tool like stunnel.
- IPv6 support. I have not tested this myself, but in theory it works.
  If you can confirm whether this works or not, please contact me.
- Optional per-address configuration. You can use different settings
  depending on the From: header.
- Multiplatform. It works on any platform Python works.
- Simple to configure.
- Short and sweet. Less than 500 lines of source code.

If you think you've found a bug or problem, read the FAQ and if that
fails, please contact me.  Click on my name in the SourceForge.net
project page to do so.


putmail queue
=============

There is a simple queuing system for putmail.py.  It consists of two
scripts: putmail_enqueue.py and putmail_dequeue.py.

To use them, you must first create the directory $HOME/.putmail/queue/.
It's recommended that only you have access to it.

Usage instructions are in the man page. Use "man putmail-queue" to read
it. It is a recommended one-time read.


Usage
-----

Installing
==========

Run install.sh (probably as root), optionally using the environment
variables PREFIX and DESTDIR to modify the installation parameters.


Configuring
===========

The manpage explains the basic configuration and all the options for the
config file. It's very easy.


Other
-----

Note
====

This [putmail](https://github.com/tgray/putmail) is a modified version
of the original putmail.py found at <http://sourceforge.net/users/rg3/>.
The github version is maintained by Tim Gray and was branched from the
original at version 1.4.The original version was written by Ricardo
Garcia Gonzalez.  All references to 'me' in this document were written
by Ricardo.


In case of problems
===================

First off, read the FAQ (at doc/FAQ or in the system's putmail.py
documentation directory). Your question may be answered there. Then,
check your putmail.py setup and try any possible valid configuration
variants.

If that doesn't help, please drop me an e-mail about the problem. My
contact information can be found at <http://sourceforge.net/users/rg3/>.
Please attach or paste any system files that may be relevant to the
problem (if they're not too big, 100 KiB can be considered the limit).


License
=======

putmail.py is distributed under the X Consortium license. Please
read the LICENSE or doc/LICENSE file.

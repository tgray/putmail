#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# putmail_enqueue.py	Read mail from standard input and save message and
#			program arguments to a mail queue.
#
# (c)	Ricardo García González
#	sarbalap-sourceforge _at_ yahoo _dot_ es
#
# This tiny script is distributed under the X Consortium License. See
# LICENSE file for more details.
#

import sys
import tempfile
import os
import os.path
import gettext
import cPickle

### Initialize ###
try:
	gettext.install("putmail_enqueue.py")	# Always before using _()
except:
	pass

### Constants ###
PUTMAIL_DIR = ".putmail"
QUEUE_SUBDIR = "queue"
HOME_EV = "HOME"
ERROR_HOME_UNSET = _("Error: %s environment variable not set") % HOME_EV
ERROR_CREATE_TEMPFILE = _("Error: unable to create file in queue")
ERROR_MESSAGE_STDIN = _("Error: unable to read message from standard input")
ERROR_DATA_OUTPUT = _("Error: unable to write data to queue file")

### Main program ###
if not os.environ.has_key(HOME_EV):
	sys.exit(ERROR_HOME_UNSET)

queue_dir = os.path.join(os.getenv(HOME_EV), PUTMAIL_DIR, QUEUE_SUBDIR)

# Create message file
try:
	(msgfd, msgfname) = tempfile.mkstemp("", "", queue_dir)
	msgfile = os.fdopen(msgfd, "w")
except (IOError, OSError):
	sys.exit(ERROR_CREATE_TEMPFILE)

# Read parameters and message contents
params = sys.argv
try:
	message = sys.stdin.read()
except IOError:
	msgfile.close()
	os.unlink(msgfname)
	sys.exit(ERROR_MESSAGE_STDIN)

# Write data
try:
	cPickle.dump((params, message), msgfile)
except IOError:
	try:
		msgfile.close()
	except:
		pass
	try:
		os.unlink(msgfname)
	except:
		pass
	sys.exit(ERROR_DATA_OUTPUT)

# Close file and exit
msgfile.close()
sys.exit()

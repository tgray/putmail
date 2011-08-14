#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# putmail_dequeue.py	Read parameters and messages from a queue and pass
#			them as arguments and standard input data to putmail.py.
#
# (c)	Ricardo García González
#	sarbalap-sourceforge _at_ yahoo _dot_ es
#
# This tiny script is distributed under the X Consortium License. See
# LICENSE file for more details.
#

import sys
import os
import os.path
import glob
import gettext
import cPickle

### Initialize ###
try:
	gettext.install("putmail_dequeue.py")	# Always before using _()
except:
	pass

### Constants ###
PUTMAIL_DIR = ".putmail"
QUEUE_SUBDIR = "queue"
HOME_EV = "HOME"
PUTMAIL_PY = "putmail.py"
ERROR_HOME_UNSET = _("Error: %s environment variable not set") % HOME_EV

### Main program ###
if not os.environ.has_key(HOME_EV):
	sys.exit(ERROR_HOME_UNSET)

# Get message file names
pattern = os.path.join(os.getenv(HOME_EV), PUTMAIL_DIR, QUEUE_SUBDIR, "*")
files = glob.glob(pattern)

# Try to send each message
(total, sent, deleted) = (0, 0, 0)
for msgfn in files:
	msgbn = os.path.basename(msgfn)
	print _("[%s] Sending message.") % msgbn

	try:
		(params, text) = cPickle.load(open(msgfn))

		# Launch putmail.py and write the message to its stdin
		cmd = "%s %s" % (PUTMAIL_PY, " ".join(params[1:]))
		child_stdin = os.popen(cmd, "w")
		child_stdin.write(text)

		exit_status = child_stdin.close()
		if not exit_status is None:
			raise Exception
		print _("[%s] Message sent.") % msgbn
		sent += 1

		try:
			print _("[%s] Deleting message file.") % msgbn
			os.unlink(msgfn)
			print _("[%s] Message deleted.") % msgbn
			deleted += 1

		except (IOError, OSError):
			print _("[%s] Message NOT deleted! Fix queue!") % msgbn

	except (IOError, OSError):
		print _("[%s] Message NOT sent.") % msgbn

	total += 1
# End of for loop

print _("Total:   %s\nSent:    %s\nDeleted: %s") % (total, sent, deleted)
sys.exit()

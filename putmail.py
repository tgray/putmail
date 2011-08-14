#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# putmail.py	Send mail read from standard input.
#
# Copyright 2007 Ricardo Garcia Gonzalez: http://sourceforge.net/users/rg3/
#
# This tiny script is distributed under the X Consortium License. See
# LICENSE file for more details.
#
# 2011-08-14 - versions > 1.4 have been slightly modified by Tim Gray.
# https://github.com/tgray/putmail

__version_info__ = (1, 4, 1)
__version__ = '.'.join([str(i) for i in __version_info__])

import ConfigParser
import smtplib
import email
import os
import sys
import socket
import datetime

import subprocess as sb
import shlex

##################################
# General program initialization #
##################################

### Some constants ###

CONFIG_DIRECTORY = '.putmail'
CONFIG_NAME = 'putmailrc'
LOG_FILE = 'putmail.log'
DEFAULT_PORT = 25
HIGHEST_PORT = 65535
FIRST_ERROR_CODE = 400

CONFIG_SECTION = 'config'
OPTION_SERVER = 'server'
OPTION_EMAIL = 'email'
OPTION_TLS = 'tls'
OPTION_LOGIN = 'username'
OPTION_PASSWORD = 'password'
OPTION_KEYCHAIN= 'keychain'
OPTION_PORT = 'port'
OPTION_QUIET = 'quiet'

FROM_HEADER = 'From'
TO_HEADER = 'To'
CC_HEADER = 'Cc'
BCC_HEADER = 'Bcc'
HOME_EV = 'HOME'

DEFAULT_CONFIG = """[config]
server = your.smtp.server.example.com
email = your.email@example.com
"""

# Internal errors
ERROR_HOME_UNSET = 'Error: %s environment variable not set' % HOME_EV
ERROR_CONFIG_NONEXISTANT = 'Error: config file %s not present'
ERROR_CONFIG_UNREADABLE = 'Error: config file present but not readable'
ERROR_CONFIG_CREATE = 'Error: unable to create sample config file'
ERROR_CONFIG_PARSE = 'Error: parse error reading config file'
ERROR_CONFIG_KEYCHAIN = 'Error: invalid keychain in config file'
ERROR_READ_MAIL = 'Error: parse error reading the mail message'
ERROR_NO_RECIPIENTS = 'Error: no recipients for the message'
ERROR_TLS = 'Error: malformed option "%s"' % OPTION_TLS
ERROR_PORT = 'Error: malformed option "%s"' % OPTION_PORT
ERROR_QUIET = 'Error: malformed option "%s"' % OPTION_QUIET
ERROR_O_OPTION = 'Error: missing option for -o'
ERROR_OPTION_ARGS = 'Error: missing arguments for last option'
ERROR_UNKNOWN_OPTION = 'Error: unknown option "%s"'

# SMTP and network errors
ERROR_REFUSED = 'Error: all recipients rejected by server'
ERROR_HELO = 'Error: server did not properly reply to HELO'
ERROR_SENDER_REFUSED = 'Error: the server rejected the envelope address'
ERROR_DISCONNECTED = 'Error: the server disconnected unexpectedly'
ERROR_DATA = 'Error: the server refused to accept the message data'
ERROR_CONNECT = 'Error: could not connect to server'
ERROR_AUTH = 'Error: server did not accept login/password'
ERROR_OTHER = 'Error: server replied: %s %s'
ERROR_NETWORK = 'Error: problem contacting server %s: %s'
ERROR_UNKNOWN = 'Error: unknown problem happened'

# Warnings
WARNING_REJECTED = 'Warning: the following recipients were rejected:'
WARNING_QUIT = 'Warning: problem disconnecting but message probably sent'
WARNING_LOGFILE = 'Warning: unable to write to log file'
WARNING_CONFIG_UNREADABLE = 'Warning: config file for %s present but no read access, falling back to default config file'
WARNING_SAMPLE_CONFIG = 'Warning: trying to create sample config file (read manpage and check permissions'

# Codes
EXIT_FAILURE = 1

### Some key variables in the program ###

theEMailAddress = None		# Envelope From address
theSMTPServer = None		# SMTP server to use
thePort = None			# The SMTP port in the server
theMessage = None		# The E-Mail message
theRecipients = []		# The recipients of the E-Mail message
theConfigFilename = None	# The configuration file name
theTLSFlag = False		# Use TLS or not
theAuthenticateFlag = False	# Use SMTP authentication or not
theSMTPLogin = None		# The login name to use with the server
theSMTPPassword = None		# The corresponding password
theRcpsFromMailFlag = False	# Take recipients from message or not
theQuietFlag = False		# Supress program output or not
theLogFile = None		# The log file name

### A few auxiliary functions ###
def handle_error(str, stderr_output, exit_program):
	fullstr = str + "\n"
	try:
		file(theLogFile, "a").write("%s: %s" %
		    (datetime.datetime.ctime(datetime.datetime.now()), fullstr))
	except (IOError, OSError):
		sys.stderr.write(WARNING_LOGFILE + "\n")

	if stderr_output:
		sys.stderr.write(fullstr)
	if exit_program:
		sys.exit(EXIT_FAILURE)

def exit_forcing_print(str):
	handle_error(str, True, True)

def exit_conditional_print(str):
	handle_error(str, not theQuietFlag, True)

def conditional_print(str):
	handle_error(str, not theQuietFlag, False)

def force_print(str):
	handle_error(str, True, False)

def check_status((code, message)):
	if code >= FIRST_ERROR_CODE:
		exit_conditional_print(ERROR_OTHER % (code, message))

def keychain(keychainType):
	if keychainType == 'osx':
		return osxkeychain

def osxkeychain(service, type="internet"):
    cmd = """/usr/bin/security find-%s-password -gs %s""" % (type, service)
    args = shlex.split(cmd)
    t = sb.check_output(args, stderr=sb.STDOUT)
    lines = t.split('\n')
    passwd = lines[0]
    passwd = passwd.split('"')[1]
    return passwd

### Check for HOME present (needed later, checking now saves a lot of work) ###
if not os.environ.has_key(HOME_EV):
	# Note: I still can't use exit_forcing_print() at this point, the log
	# filename is not set.
	sys.exit(ERROR_HOME_UNSET + "\n")

### Build the log filename now ###
theLogFile = os.path.join(os.environ[HOME_EV], CONFIG_DIRECTORY, LOG_FILE)

###############################################
# First step: Parse the command line options. #
###############################################

### This is the new manual option parser to fully comply with	###
### the braindead traditional sendmail options format >:(	###

try:

	program_args = sys.argv[1:]	# Program arguments
	print_info = False		# prints program information
	direct_exit = False		# Exit directly?

	### The lists below contain IGNORED OPTIONS ONLY, see the loop.	###
	### Option groups ending with _exit make the program exit	###
	### directly at the end of the parsing loop			###

	single_options = ['-Ac', '-Am', '-ba', '-bm', '-bs', '-bt',
				'-bv', '-G', '-i', '-n', '-v']

	single_options_exit = ['-bd', '-bD', '-bh', '-bH', '-bp', '-bP', '-qf',
				'-bi' ]

	one_argument_options = [ '-B', '-C', '-D', '-d', '-F', '-h', '-L', '-N',
				'-O', '-p', '-R', '-r', '-V', '-X' ]

	one_argument_options_exit = ['-qG', '-qI', '-qQ', '-qR', '-qS', '-q!I',
					'-q!Q', '-q!R', '-q!S' ]

	optional_extra_chars_options_exit = [ '-q', '-qp', '-Q' ]

	# Eat arguments until there's none left
	while (len(program_args) > 0):
		if program_args[0] == '--': # Remaining options are recipients
			theRecipients.extend(program_args[1:])
			break
		elif program_args[0] == '--version':
			print_info = True
			direct_exit = True
			break
		elif program_args[0] == '-t': # Take recipients from message
			theRcpsFromMailFlag = True
			del program_args[0]
		elif program_args[0] in single_options:
			del program_args[0]
		elif program_args[0] in single_options_exit:
			del program_args[0]
			direct_exit = True
		elif program_args[0] == '-f': # Address in next argument
			theEMailAddress = program_args[1]
			del program_args[0]
			del program_args[0]
		elif program_args[0][0:2] == '-f': # Address in this argument
			theEMailAddress = program_args[0][2:]
			del program_args[0]
		elif program_args[0] in one_argument_options:
			del program_args[0]
			del program_args[0]
		elif program_args[0][0:2] in one_argument_options:
			del program_args[0]
		elif program_args[0] in one_argument_options_exit:
			del program_args[0]
			del program_args[0]
			direct_exit = True
		elif (sum([program_args[0].startswith(x) # First chars match
			   for x in one_argument_options_exit]) > 0):
			del program_args[0]
			direct_exit = True
		elif (sum([program_args[0].startswith(x) # First chars match
			   for x in optional_extra_chars_options_exit]) > 0):
			del program_args[0]
			direct_exit = True
		elif program_args[0].startswith('-o'):	# Weird case
			if program_args[0] == '-o':
				exit_forcing_print(ERROR_O_OPTION)
			del program_args[0]
			del program_args[0]
		else:
			if program_args[0].startswith('-'):
				exit_forcing_print(ERROR_UNKNOWN_OPTION %
							program_args[0])
			theRecipients.append(program_args[0])
			del program_args[0]
	# End of parsing loop

# Problem in some option argument
except IndexError:
	exit_forcing_print(ERROR_OPTION_ARGS)

# print program info
if print_info:
	programName = os.path.basename(sys.argv[0])
	version = "%s %s" % (programName, __version__)
	print version
	print "  type `man %s` for more information" % programName

# Options indicated direct exit
if direct_exit:
	sys.exit()

# No addresses found?
if len(theRecipients) == 0 and not theRcpsFromMailFlag:
	exit_forcing_print(ERROR_NO_RECIPIENTS)

######################################################
# Second step: Read the message from standard input. #
######################################################

try:
	theMessage = email.message_from_file(sys.stdin)
except email.Errors.MessageError:
	exit_forcing_print(ERROR_READ_MAIL)


############################################
# Third step: Read the configuration file. #
############################################

### Try to find the apropiate configuration file or	###
### fall back to CONFIG_NAME.				###

configPath = os.path.join(os.environ[HOME_EV], CONFIG_DIRECTORY) # temporally
theConfigFilename = CONFIG_NAME
if theMessage.has_key(FROM_HEADER):
	try:
		fromaddr = email.Utils.getaddresses(
			theMessage.get_all(FROM_HEADER))[-1][1]
		tmpcfgpath = os.path.join(configPath, fromaddr)
		if os.path.isfile(tmpcfgpath):
			if os.access(tmpcfgpath, os.R_OK):
				theConfigFilename = fromaddr
			else:
				force_print(WARNING_CONFIG_UNREADABLE %fromaddr)
				
	except IndexError:
		pass

configPath = os.path.join(configPath, theConfigFilename) # finally

if not os.path.exists(configPath):
	# Config file not present, try to create one and exit
	force_print(ERROR_CONFIG_NONEXISTANT % configPath)
	force_print(WARNING_SAMPLE_CONFIG)

	try:
		dirname = os.path.dirname(configPath)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
		file(configPath, "w").write(DEFAULT_CONFIG)
	except:
		exit_forcing_print(ERROR_CONFIG_CREATE)

	sys.exit(EXIT_FAILURE)

# Last check. If we cannot read this we cannot proceed.
if not os.access(configPath, os.R_OK):
	exit_forcing_print(ERROR_CONFIG_UNREADABLE)

### Read the file ###

config = ConfigParser.ConfigParser()
try:
	config.read([configPath])
except:
	exit_forcing_print(ERROR_CONFIG_PARSE)

### Check conditions for bad configurations ###

if (not config.has_section(CONFIG_SECTION) or
		not config.has_option(CONFIG_SECTION, OPTION_SERVER) or
		not config.has_option(CONFIG_SECTION, OPTION_EMAIL) or
		(config.has_option(CONFIG_SECTION, OPTION_LOGIN) and
		 not (config.has_option(CONFIG_SECTION, OPTION_PASSWORD) or
			 config.has_option(CONFIG_SECTION, OPTION_KEYCHAIN))) or
		 ((config.has_option(CONFIG_SECTION, OPTION_PASSWORD) or
			 config.has_option(CONFIG_SECTION, OPTION_KEYCHAIN)) and not
			 config.has_option(CONFIG_SECTION, OPTION_LOGIN))):
	exit_forcing_print(ERROR_CONFIG_PARSE)

### Extract the necessary configuration parameters ##

theSMTPServer = config.get(CONFIG_SECTION, OPTION_SERVER)

if theEMailAddress is None:	# "Envelope from" if -f was not present
	theEMailAddress = config.get(CONFIG_SECTION, OPTION_EMAIL)

try:	# TLS
	if (config.has_option(CONFIG_SECTION, OPTION_TLS) and
			config.getboolean(CONFIG_SECTION, OPTION_TLS)):
		theTLSFlag = True
except ValueError:
	exit_forcing_print(ERROR_TLS)

try:	# Quiet
	if (config.has_option(CONFIG_SECTION, OPTION_QUIET) and
			config.getboolean(CONFIG_SECTION, OPTION_QUIET)):
		theQuietFlag = True
except ValueError:
	exit_forcing_print(ERROR_QUIET)

if config.has_option(CONFIG_SECTION, OPTION_LOGIN):	# Login/password
	theSMTPLogin = config.get(CONFIG_SECTION, OPTION_LOGIN)
	try:
		# if config.has_option(CONFIG_SECTION, OPTION_KEYCHAIN):
		keychainType = config.get(CONFIG_SECTION, OPTION_KEYCHAIN)
		keychain_func = keychain(keychainType)
		theSMTPPassword = keychain_func(theSMTPServer)
	except TypeError:
		exit_forcing_print(ERROR_CONFIG_KEYCHAIN)
	except ConfigParser.NoOptionError:
		theSMTPPassword = config.get(CONFIG_SECTION, OPTION_PASSWORD)
	theAuthenticateFlag = True

try:	# Port
	if config.has_option(CONFIG_SECTION, OPTION_PORT):
		thePort = config.getint(CONFIG_SECTION, OPTION_PORT)
		if thePort < 0 or thePort > HIGHEST_PORT:
			raise ValueError
	else:
		thePort = DEFAULT_PORT
except ValueError:
	exit_forcing_print(ERROR_PORT)

##########################################################################
# Fourth step:	Extract information from important headers (like To) and #
#		remove the Bcc header from the message.			 #
##########################################################################

# If we are told to take the addresses from the message itself...
if theRcpsFromMailFlag:
	if theMessage.has_key(TO_HEADER):
		theRecipients.extend(
			[x[1] for x in email.Utils.getaddresses(
				theMessage.get_all(TO_HEADER))]
		)
	if theMessage.has_key(CC_HEADER):
		theRecipients.extend(
			[x[1] for x in email.Utils.getaddresses(
				theMessage.get_all(CC_HEADER))]
		)
	if theMessage.has_key(BCC_HEADER):
		theRecipients.extend(
			[x[1] for x in email.Utils.getaddresses(
				theMessage.get_all(BCC_HEADER))]
		)

# Delete Bcc header if it exists
if theMessage.has_key(BCC_HEADER):
	del theMessage[BCC_HEADER]

# Still no addresses found?
if len(theRecipients) == 0:
	exit_forcing_print(ERROR_NO_RECIPIENTS)

####################################################
# Fifth step: Send the damned message finally \o/. #
####################################################

try:
	server = smtplib.SMTP()
	#server.set_debuglevel(True)
	check_status(server.connect(theSMTPServer, thePort))
	check_status(server.ehlo())
	if theTLSFlag:
		check_status(server.starttls())
		check_status(server.ehlo()) # Repeat EHLO after starting TLS
	if theAuthenticateFlag:
		check_status(server.login(theSMTPLogin, theSMTPPassword))
	rejected = server.sendmail(theEMailAddress, theRecipients,
					theMessage.as_string())
except smtplib.SMTPServerDisconnected:
	exit_conditional_print(ERROR_DISCONNECTED)
except smtplib.SMTPSenderRefused:
	exit_conditional_print(ERROR_SENDER_REFUSED)
except smtplib.SMTPRecipientsRefused:
	exit_conditional_print(ERROR_REFUSED)
except smtplib.SMTPDataError:
	exit_conditional_print(ERROR_DATA)
except smtplib.SMTPConnectError:
	exit_conditional_print(ERROR_CONNECT)
except smtplib.SMTPHeloError:
	exit_conditional_print(ERROR_HELO)
except smtplib.SMTPAuthenticationError:
	exit_conditional_print(ERROR_AUTH)
except smtplib.SMTPResponseException, err:
	exit_conditional_print(ERROR_OTHER % (err.smtp_code, err.smtp_error))
except (socket.error, socket.herror, socket.gaierror), err:
	exit_conditional_print(ERROR_NETWORK % (theSMTPServer, err[1]))
except socket.timeout, err:
	exit_conditional_print(ERROR_NETWORK % (theSMTPServer, err))
except smtplib.SMTPException:
	exit_conditional_print(ERROR_UNKNOWN)

try:
	server.quit()
except:
	conditional_print(WARNING_QUIT)

# Check for rejected recipients
if len(rejected) > 0:
	conditional_print(WARNING_REJECTED)
	conditional_print('\n'.join(['\t' + email for email in rejected]))

# Good enough
sys.exit()
# vim: set ft=python noet sts=4 sw=4 ts=4 : 

#!/usr/bin/python2
"""
TwilightPam
Based on STAMP by Chokepoint.
Only real modification to date is changing it to use Twilio.
Todo:
> Code Cleanup
> More Error Handling
> ???????
> PROFIT!!!
"""
from twilio.rest import TwilioRestClient
import random
import string
import hashlib
import pwd
import syslog

# Globals: Dirty.
account_sid = "ACXXXXXXXXXXXXXXXXX"
auth_token = "YYYYYYYYYYYYYYYYYY"
sender_phone = "000000000000000"


def send_sms(phone, pin):
    client = TwilioRestClient(account_sid, auth_token)
    message = client.messages.create(to=phone, from_==sender_phone, body=pin)

def auth_log(msg):
	"""Send errors to default auth log"""
	syslog.openlog(facility=syslog.LOG_AUTH)
	syslog.syslog("TWILIGHTPAM: " + msg)
	syslog.closelog()

def get_hash(plain_text):
	"""return sha512 digest of given plain text"""
	key_hash = hashlib.sha512()
	key_hash.update(plain_text)
	
	return key_hash.digest()

def get_user_number(user):
	"""Extract user's phone number for pw entry"""
	try:
		comments = pwd.getpwnam(user).pw_gecos
	except KeyError: # Bad user name
		auth_log("No local user (%s) found." % user)
		return -1
	
	try:
		return comments.split(',')[2] # Return Office Phone
	except IndexError: # Bad comment section format
		auth_log("Invalid comment block for user %s. Phone number must be listed as Office Phone" % (user))
		return -1
		
def gen_key(user, user_number, length):
	"""Generate the key and send text to the user's phone"""
	pin = ''.join(random.choice(string.digits) for i in range(length))
	try:
		send_sms(phone=user_number, pin=pin)
	except:
		if not user_number:
			auth_log("No phone number listed for user (%s)." % (user))
		else:
			auth_log("Error sending PIN to the given SMS number. (%s)" % (user_number))
		return -1
		
	return get_hash(pin)
	
def pam_sm_authenticate(pamh, flags, argv):
	PIN_LENGTH = 8 # Length of one time PIN
	try:
		user = pamh.get_user()
		user_number = get_user_number(user)
	except pamh.exception, e:
		return e.pam_result
	
	if user is None or user_number == -1:
		msg = pamh.Message(pamh.PAM_ERROR_MSG, "Unable to send one time PIN.\nPlease contact your System Administrator")
		pamh.conversation(msg)
		return pamh.PAM_ABORT
		
	pin = gen_key(user, user_number, PIN_LENGTH)
	if pin == -1: # One time PIN could not be generated
		msg = pamh.Message(pamh.PAM_ERROR_MSG, "Unable to send one time PIN.\nPlease contact your System Administrator")
		pamh.conversation(msg)
		return pamh.PAM_ABORT
		
	for attempt in range(0,3): # 3 attempts to enter the one time PIN
		msg = pamh.Message(pamh.PAM_PROMPT_ECHO_OFF, "Enter one time PIN: ")
		resp = pamh.conversation(msg)

		if get_hash(resp.resp) == pin:
			return pamh.PAM_SUCCESS
		else:
			continue
	return pamh.PAM_AUTH_ERR

def pam_sm_setcred(pamh, flags, argv):
	return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
	return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
	return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
	return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
	return pamh.PAM_SUCCESS

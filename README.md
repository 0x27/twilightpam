twilightpam
===========

Python-PAM 2-Factor Authentication using Twilio

# What?
After reading the sourcecode for [Stampauth][stampauth] by [Chokepoint][chokepoint] I decided it would be nice to expand it to use the Twilio API to send SMS messages, as the txtdrop solution they were using did not support Ireland. I also had a need to test out the Twilio API for an upcoming project.

Therefore, I simply made this fork of it. All credit for the original idea and code goes to [Chokepoint][chokepoint], I simply ported it to use Twilio.

#Setup:
First we install the dependencies...
```
$ sudo apt-get install python-pam
$ pip install twilio
```

Next we download and install twilightpam
```
$ git clone https://github.com/0x27/twilightpam.git
$ cd twilightpam
$ sudo cp twilightpam.py /lib/security/
```

Next edit the "sender_phone", "account_sid", "auth_token" lines in /lib/security/twilightpam.py

Next we configure the sshd config for using this auth.

In /etc/ssh/sshd_config uncomment the following line:
```
ChallengeResponseAuthentication yes
```

In /etc/pam.d/sshd locate the section marked with "@include common-auth" and make it look like the entry below.

```
auth       requisite     pam_python.so twilightpam.py
@include common-auth
```

You can set a users Office Phone number using the following:
```
sudo usermod user -c ',,+353851234567,'
```

Assuming all goes to plan, after you restart sshd, next time you try log in it *should* send you a SMS message with a one time key for the second factor in authentication.

# Bugs
None known of yet, make an issue if you find any :)

# Licence
Licenced under the [WTFPL][wtfpl] because I don't give a fuck what you do.

[stampauth]: https://github.com/chokepoint/stampauth
[chokepoint]: http://www.chokepoint.net/
[wtfpl]: http://wtfpl.net

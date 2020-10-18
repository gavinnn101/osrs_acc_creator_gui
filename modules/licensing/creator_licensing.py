# CryptoLens.io
# pip install licensing
import sys

from licensing.models import *
from licensing.methods import Key, Helpers
from configparser import ConfigParser

RSAPubKey = "<RSAKeyValue><Modulus>vAso8AeR2Opqu3B4seh9fOsdYFTp0pNkMt8agYxzN3mwx8jJ8HY4dc8vrMAFQSaKzLDLUR4XFNasa4/slf/fSkWK2SfarWOoyoc4QF9rfWTWScNVXx4MYLasCi1IWKm9f03QQyZFKlmalvpXqfhR61sg0WnKPUw+J4L4qm95nAixk8u+rMtN+uhETNo0dOVAAjm9rjchTE9HKuQJGmTvTWAiO0QlAUi6Myguurpm0wTM14PVIhy4LAYtMV4zDfz4evVnFeS/Ca0xDFraJprdwzdWaLkHVTT2H0Qr4zTX2gLh0hzwYSjauckRXQmwgER3hGRuJp880OYRrTQdSzFhWw==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"
auth = "WyIxNjkyMTEiLCJVVkpRcXRDMWh6R0lRajJEQWdud0liclFHb09kQUtMMjhhRzRpTU1zIl0="

def get_license_settings():
	"""Gets and returns the License settings from settings.ini"""
	config = ConfigParser()
	try:
		config.read('settings/settings.ini')
	except FileNotFoundError:
		sys.exit("settings.ini file not found. "
				 "Make sure it's in the same directory.")

	license_key = config['LICENSE_SETTINGS'].get('license_key')

	return license_key


def check_key():
    license_key = get_license_settings()
    result = Key.activate(token=auth,\
                    rsa_pub_key=RSAPubKey,\
                    product_id=8237, \
                    key=license_key,\
                    machine_code=Helpers.GetMachineCode())

    if result[0] == None or not Helpers.IsOnRightMachine(result[0]):
        # an error occurred or the key is invalid or it cannot be activated
        # (eg. the limit of activated devices was achieved)
        return False
    else:
        # everything went fine if we are here!
        license_key = result[0]
        return True

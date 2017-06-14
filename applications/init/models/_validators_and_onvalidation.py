# """
# def _on_validation_send(form):
#     text = ""
#     for each in sorted(form.vars.keys()):
#         try:  # extract password from LAZYCRYPT object
#             value = form.vars[each].password
#         except AttributeError:
#             value = form.vars[each]
#         text += "%s: %s\n" % (each, value)
#
#     mail.settings.cipher_type = 'x509'
#     mail.settings.sign = True
#     mail.settings.sign_passphrase = 'asdfe34Ddefe'
#     mail.settings.encrypt = True
#     mail.settings.x509_sign_keyfile = 'private.key'
#     mail.settings.x509_sign_certfile = 'public.cert'
#     mail.settings.x509_crypt_certfiles = ['himel.cert']
#     #OPENSSL_Uplink(00007FFA33852000,08): no OPENSSL_Applink
#     #mail.settings.cipher_type = 'x509';mail.settings.sign = False;mail.settings.encrypt = True;mail.settings.x509_crypt_certfiles = ['himel.cer'];mail.send(to=['himel@insightmanagement.org'], subject='A')
#     if not mail.send(to=['himel@insightmanagement.org'], subject='Answer for question ID: "%s"' % form.attributes.get("_id"), message=text):
#         form.errors.note = mail.error
#
# import gnupg
# gpg = gnupg.GPG()
#
# class _sample_validator:
#     def __init__(self, recipient_keys, error_message='Encryption error'):
#         self.recipient_keys = recipient_keys
#         self.error_message = error_message
#     def __call__(self, value):
#         output = gpg.encrypt(value, self.recipient_keys)
#         if output:
#             return (output, None)
#         else:
#             return (output, self.error_message)
#     def formatter(self, value):
#         return gpg.decrypt(value)
# """


import gnupg

gpg = gnupg.GPG()


def _on_validation_filename(form):
    form.vars.filename = request.vars.upload.filename


def _validate_start_end_time(form, start_field_name="start_time", end_field_name="end_time"):
    # get the actual datetime.time object and compare
    if form.vars[start_field_name] >= form.vars[end_field_name]:
        form.errors[end_field_name] = "End time must be after start time!"


def _on_validation_crypt(table_name):
    """must initialize GPG public key to system's GPG keys...
    gpg = gnupg.GPG()
    #on local system, generate public/private keys (certificate) in kleopatra or do it in python http://bit.ly/2iyal7g
    gpg.export_keys("3E2FD6EB", False)  # pass id of the certificate, get public key # True will return private key
    u'-----BEGIN PGP PUBLIC KEY BLOCK-----\r\nVersion: GnuPG v2\r\n\r\nmQENBFf0YFcBCA...... #key_data
    #on remote system import the public key
    gpg.import_keys(key_data)
    """
    def inner(form):
        plaintext = ""
        for each in sorted(form.vars.keys()):
            try:
                value = form.vars[each].password  # try to get password from LAZYCRYPT object
            except AttributeError:
                value = form.vars[each]
            plaintext += "%s: %s\n" % (each, value)  # keys.gnupg.net
        encrypted = gpg.encrypt(plaintext, "ECA488E9")  # change latter to list of private keys approved via rbac
        db[table_name].insert(gpg_encrypted=encrypted, application=APP_ID)
    return inner


class IS_DIGITS:
    def __init__(self, length=None, error_message='Must be all digits'):
        self.l = length
        self.e = error_message + " of length %s!" % length if length else error_message + "!"

    def __call__(self, value):
        if (value and all(map(lambda d: d.isdigit(), value))) and (not self.l or len(value) == self.l):
            return value, None
        return value, self.e


_am_pm_time_validator = IS_TIME("Enter time as HH:MM [AM/PM]")

DATE_VALIDATOR = IS_DATE(format=T('%m/%d/%Y'), error_message='must be MM/DD/YYYY!')
import gnupg
gpg = gnupg.GPG()

_telephone_field_validator = requires=IS_MATCH('\([0-9][0-9][0-9]\)[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]',
                                               error_message='Use the format (123)456-7890 (no spaces)')

_note_field = Field("note", label=XML("<span class='text-muted'>Note</span>"), comment="Optional")

_yes_no_field_default = Field("please_choose", requires=IS_IN_SET(["Yes", "No"]), comment=XML("<span class='visible-print-inline'>Yes or No.</span>"))

"""
def _on_validation_send(form):
    text = ""
    for each in sorted(form.vars.keys()):
        try:  # extract password from LAZYCRYPT object
            value = form.vars[each].password
        except AttributeError:
            value = form.vars[each]
        text += "%s: %s\n" % (each, value)

    mail.settings.cipher_type = 'x509'
    mail.settings.sign = True
    mail.settings.sign_passphrase = 'asdfe34Ddefe'
    mail.settings.encrypt = True
    mail.settings.x509_sign_keyfile = 'private.key'
    mail.settings.x509_sign_certfile = 'public.cert'
    mail.settings.x509_crypt_certfiles = ['himel.cert']
    #OPENSSL_Uplink(00007FFA33852000,08): no OPENSSL_Applink
    #mail.settings.cipher_type = 'x509';mail.settings.sign = False;mail.settings.encrypt = True;mail.settings.x509_crypt_certfiles = ['himel.cer'];mail.send(to=['himel@insightmanagement.org'], subject='A')
    if not mail.send(to=['himel@insightmanagement.org'], subject='Answer for question ID: "%s"' % form.attributes.get("_id"), message=text):
        form.errors.note = mail.error

import gnupg
gpg = gnupg.GPG()

class _sample_validator:
    def __init__(self, recipient_keys, error_message='Encryption error'):
        self.recipient_keys = recipient_keys
        self.error_message = error_message
    def __call__(self, value):
        output = gpg.encrypt(value, self.recipient_keys)
        if output:
            return (output, None)
        else:
            return (output, self.error_message)
    def formatter(self, value):
        return gpg.decrypt(value)
"""


def _on_validation_filename(form):
    form.vars.filename = request.vars.upload.filename
    _on_validation_generic(form)


def _on_validation_generic(form):
    form.vars.application = APP_ID


def _on_validation_crypt(table_name):
    def inner(form):
        plaintext = ""
        for each in sorted(form.vars.keys()):
            try:
                value = form.vars[each].password  #try to get password from LAZYCRYPT object
            except AttributeError:
                value = form.vars[each]
            plaintext += "%s: %s\n" % (each, value)
        encrypted = gpg.encrypt(plaintext, "7AA8DBFE")  #change latter to list of private keys approved via rbac
        db[table_name].insert(gpg_encrypted=encrypted, application=APP_ID)
    return inner

class _IS_DIGITS:
    def __init__(self, length=None, error_message='Must be all digits'):
        self.l = length
        self.e = error_message + " of length %s!" % length if length else error_message + "!"
    def __call__(self, value):
        if (value and all(map(lambda d: d.isdigit(), value))) and (not self.l or len(value) == self.l):
            return (value, None)
        return (value, self.e)

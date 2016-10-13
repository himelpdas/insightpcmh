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
"""

def _on_validation_filename(form):
    form.vars.filename = request.vars.upload.filename


import gnupg
gpg = gnupg.GPG()


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
        db[table_name].insert(gpg_encrypted=encrypted)
    return inner
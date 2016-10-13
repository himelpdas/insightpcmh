class _IS_DIGITS:
    def __init__(self, length=None, error_message='Must be all digits'):
        self.l = length
        self.e = error_message + " of length %s!" % length if length else error_message + "!"
    def __call__(self, value):
        if (value and all(map(lambda d: d.isdigit(), value))) and (not self.l or len(value) == self.l):
            return (value, None)
        return (value, self.e)
"""
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
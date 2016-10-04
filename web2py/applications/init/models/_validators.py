class _IS_DIGITS:
    def __init__(self, length=None, error_message='Must be all digits'):
        self.l = length
        self.e = error_message + " of length %s!" % length if length else error_message + "!"
    def __call__(self, value):
        if (value and all(map(lambda d: d.isdigit(), value))) and (not self.l or len(value) == self.l):
            return (value, None)
        return (value, self.e)

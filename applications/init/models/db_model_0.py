LIST_OF_STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
                   "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                   "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                   "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                   "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

FAKE_DB = {}


# (emr)###################################################

db.define_table("account_created",
    
    YES_NO_FIELD,
    
    auth.signature
)


FAKE_DB.update({"emr_credentials": [
    Field("username", requires=IS_NOT_EMPTY()),
    Field("password", requires=IS_NOT_EMPTY(), widget=SQLFORM.widgets.password.widget),
    Field("verify_password", requires=[IS_EQUAL_TO(request.vars.password), IS_NOT_EMPTY()],
          widget=SQLFORM.widgets.password.widget),
    NOTE_FIELD,
    auth.signature
]})


db.define_table("emr_credentials",
    Field("gpg_encrypted", "text"),
    auth.signature
)

db.define_table(  # todo - change back to gpg when gnupg binary and gpg certificate is fixed
    "emr_login", 
    Field("website"),
    Field("username", requires=IS_NOT_EMPTY()),
    Field("password", requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
)

# (credit_card)###################################################

FAKE_DB.update({"credit_card": [
    Field("account_holder", requires=IS_NOT_EMPTY(), comment="Must match exact name on card."),
    Field("expiration_month", requires=IS_IN_SET(range(1, 13), zero=None)),
    Field("expiration_year", requires=[IS_LENGTH(4, 4),  IS_INT_IN_RANGE(2000, 2100,
                                                                         error_message='4-digit year required!')]),
    Field("card_number", requires=IS_NOT_EMPTY(), widget=SQLFORM.widgets.password.widget),
    Field("verify_card_number", requires=[IS_EQUAL_TO(request.vars.card_number), IS_NOT_EMPTY()],
          widget=SQLFORM.widgets.password.widget),
    Field("cvv_code", requires=IS_NOT_EMPTY(), widget=SQLFORM.widgets.password.widget),
    NOTE_FIELD,
    auth.signature
]})


db.define_table("credit_card",
    
    Field("gpg_encrypted", "text"),
    auth.signature
)
_list_of_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
                   "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                   "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                   "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                   "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

db.define_table("practice_info",
    Field("application", 'reference application', readable=False, writable=False),
    Field("practice_name", requires=IS_NOT_EMPTY()),
    Field("practice_specialty",
          requires=IS_IN_SET(['Internal Medicine', 'Pediatrics', 'Family Medicine'], sort=True, zero=None)),
    Field("phone", requires=_telephone_field_validator),
    Field("extension", requires=IS_EMPTY_OR(_IS_DIGITS()), comment="Optional"),
    Field("address_line_1", requires=IS_NOT_EMPTY()),
    Field("address_line_2", comment="Optional"),
    Field("city", requires=IS_NOT_EMPTY()),
    Field("state_", label="State", requires=IS_IN_SET(_list_of_states, zero=None)),
    Field("website", requires=IS_EMPTY_OR(IS_URL()), comment="Optional"),
    _note_field,
    # auth.signature  # not needed because db._common_fields.append(auth.signature)
)

# _practice = db(db.practice_info.id > 0).select().last() or Storage(practice_name="The practice")

db.define_table("primary_contact",
    Field("application", 'reference application', readable=False, writable=False),
    Field("first_name", requires=IS_NOT_EMPTY()),
    Field("last_name", requires=IS_NOT_EMPTY()),
    Field("email", requires=IS_EMAIL()),
    Field("phone", requires=IS_EMPTY_OR(_telephone_field_validator),
          comment="Leave blank if same as practice number"),
    Field("extension", requires=IS_EMPTY_OR(_IS_DIGITS()), comment="Optional"),
    Field("role", requires=IS_IN_SET(["MD", "PA", "MA", "Manager", "Other"], sort=True, zero=None)),
    _note_field,
    # auth.signature  # not needed because db._common_fields.append(auth.signature)
)


db.define_table("clinical_hour",
    Field("application", 'reference application', readable=False, writable=False),
    _day_of_week_field(),
    Field("start_time", "time", requires=_am_pm_time_validator, label="Opens"),
    Field("end_time", "time", requires=_am_pm_time_validator, label="Closes"),
    _note_field,
    # auth.signature  # not needed because db._common_fields.append(auth.signature)
)


db.define_table("billing_provider",
    Field("application", 'reference application', readable=False, writable=False),
    Field("first_name", requires=IS_NOT_EMPTY()),
    Field("last_name", requires=IS_NOT_EMPTY()),
    Field("email", requires=IS_EMAIL()),
    Field("npi", label='NPI#', requires=IS_NOT_EMPTY()),
    Field("dea", label='DEA#', requires=IS_NOT_EMPTY()),
    Field("license", label='License #', requires=IS_NOT_EMPTY()),
    Field("role", requires=IS_IN_SET(["MD", "DO", "NP", "PA"], sort=True, zero=None)),
    _days_of_week_field(label="Typical days",
                        comment="Select the days when patients are usually seen by this provider"),
    Field("job_description", 'text', comment=XML("Enter a brief description of the <b>patient-centered</b>"
                                                 " tasks this provider conducts <i>(i.e. tracks referrals, "
                                                 "makes call-backs, etc.)</i> outside of an examination."),
          requires=IS_LENGTH(minsize=140, maxsize=1000)),
    _note_field,
    # auth.signature  # not needed because db._common_fields.append(auth.signature)
)


db.define_table("has_staff",
    Field("application", 'reference application', readable=False, writable=False),
    _yes_no_field_default,
    _note_field,
    auth.signature
)


db.define_table("staff",
    Field("application", 'reference application', readable=False, writable=False),
    Field("first_name", requires=IS_NOT_EMPTY()),
    Field("last_name", requires=IS_NOT_EMPTY()),
    Field("role", requires=IS_IN_SET(
        sorted(["MA", "PA", "Manager", "Intern", "Phlebotomist", "Front Desk", "Other (please describe)"]),
        zero=None)),
    _days_of_week_field(label="Typical days",
                        comment="Select the days when this non-provider is usually at the office"),
    Field("job_description", 'text', comment=XML("Enter a brief description of the <b>patient-centered</b>"
                                                 " tasks this employee conducts <i>(i.e. tracks referrals, "
                                                 "makes call-backs, etc.)</i>."),
          requires=IS_LENGTH(minsize=140, maxsize=1000)),
    _note_field,
    auth.signature
)


db.define_table("emr",
    Field("application", 'reference application', readable=False, writable=False),
    Field("name",
          requires=IS_IN_SET(['eClinicalWorks', 'MDLand', 'HealthFusion', 'Other'], sort=True, zero=None)),
    _note_field,
    auth.signature
)


db.define_table("account_created",
    Field("application", 'reference application', readable=False, writable=False),
    _yes_no_field_default,
    _note_field,
    auth.signature
)


_fake_db = {}


_fake_db.update({"emr_credentials": [
    Field("username", requires=IS_NOT_EMPTY()),
    Field("password", requires=IS_NOT_EMPTY(), widget=SQLFORM.widgets.password.widget),
    Field("verify_password", requires=[IS_EQUAL_TO(request.vars.password), IS_NOT_EMPTY()],
          widget=SQLFORM.widgets.password.widget),
    _note_field,
    auth.signature
]})


db.define_table("emr_credentials",
    Field("application", 'reference application', readable=False, writable=False),
    Field("gpg_encrypted", "text"),
    auth.signature
)

_fake_db.update({"credit_card": [
    Field("account_holder", requires=IS_NOT_EMPTY(), comment="Must match exact name on card."),
    Field("expiration_date", 'date', requires=IS_NOT_EMPTY(), comment=XML("Day is <b>not</b> important.")),
    Field("card_number", requires=IS_NOT_EMPTY(), widget=SQLFORM.widgets.password.widget),
    Field("verify_card_number", requires=[IS_EQUAL_TO(request.vars.card_number), IS_NOT_EMPTY()],
          widget=SQLFORM.widgets.password.widget),
    _note_field,
    auth.signature
]})


db.define_table("credit_card",
    Field("application", 'reference application', readable=False, writable=False),
    Field("gpg_encrypted", "text"),
    auth.signature
)

# (ncqa login)###################################################

_fake_db.update({"ncqa_app": [
    Field("username", requires=IS_NOT_EMPTY()),
    Field("password", requires=IS_NOT_EMPTY(), widget=SQLFORM.widgets.password.widget),
    Field("verify_password", requires=[IS_EQUAL_TO(request.vars.password), IS_NOT_EMPTY()],
          widget=SQLFORM.widgets.password.widget),
    _note_field,
    auth.signature
]})


db.define_table("ncqa_app",
    Field("application", 'reference application', readable=False, writable=False),
    Field("gpg_encrypted", "text"),
    auth.signature
)

_fake_db.update({"ncqa_iss": [
    Field("username", requires=IS_NOT_EMPTY()),
    Field("password", requires=IS_NOT_EMPTY(), widget=SQLFORM.widgets.password.widget),
    Field("verify_password", requires=[IS_EQUAL_TO(request.vars.password), IS_NOT_EMPTY()],
          widget=SQLFORM.widgets.password.widget),
    _note_field,
    auth.signature
]})


db.define_table("ncqa_iss",
    Field("application", 'reference application', readable=False, writable=False),
    Field("gpg_encrypted", "text"),
    auth.signature
)

# (no shows)###################################################

db.define_table("no_shows_training",
    Field("application", 'reference application', readable=False, writable=False),
    _yes_no_field_default,
    _note_field,
    auth.signature
)

db.define_table("pace_holder",
    Field("application", 'reference application', readable=False, writable=False),
    _yes_no_field_default,
    _note_field,
    auth.signature
)

# (availability of appointments)###################################################
_within = IS_IN_SET([(0, "Same Day"), (1, "1 Day"), (2, "2 Days"), (3, "3 Days"), (4, "4 Days"), (5, "5 Days"),
                     (6, "6 Days"), (7, "7 Days (1 Week)"), (10, "1.5 Weeks"), (14, "2 Weeks"),
                     (21, "3 Weeks")], zero=None)
db.define_table("availability_of_appointments",
    Field("application", 'reference application', readable=False, writable=False),
    Field("new_patient", requires=_within),
    Field("urgent", requires=_within),
    Field("consult", requires=_within),
    Field("walk_in", requires=_within),
    Field("same_day", requires=_within),
    _note_field,
    auth.signature
)

# (4)###################################################


# (5)###################################################


# (end)###################################################
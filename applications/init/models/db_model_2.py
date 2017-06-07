staff_format = '%(first_name)s %(last_name)s (%(role)s)'
db.define_table(
    "provider",
    APP_FIELD,
    Field("first_name", requires=IS_NOT_EMPTY()),
    Field("last_name", requires=IS_NOT_EMPTY()),
    Field("email", requires=IS_EMAIL()),
    Field("npi", label='NPI#'),  # requires=IS_NOT_EMPTY()),
    Field("dea", label='DEA#'),  # requires=IS_NOT_EMPTY()),
    Field("license", label='License #'),  # requires=IS_NOT_EMPTY()),
    Field("role", requires=IS_IN_SET(["MD", "DO", "APRN (i.e. NP)", "PA"], sort=True, zero=None)),
    Field("bills_under", 'list:reference provider', label='Bills Under / Shares Patients Under'),
    DAYS_OF_WEEK_FIELD(label="Official days",
                       comment="Only select the days when patients are seen by this provider"),
    # Field("job_description", 'text', comment=XML("Enter a brief description of the <b>patient-centered</b>"
    #                                              " tasks this provider conducts <i>(i.e. tracks referrals, "
    #                                              "makes call-backs, etc.)</i> outside of an examination."),
    #      requires=IS_LENGTH(minsize=140, maxsize=1000)),
    NOTE_FIELD,
    format=staff_format,
    # auth.signature  # not needed because db._common_fields.append(auth.signature)
)

db.provider.bills_under.requires = IS_IN_DB(db(db.provider.application == APP_ID), 'provider.application',
                                            staff_format, multiple=True)


db.define_table(
    "other_staff",
    APP_FIELD,
    YES_NO_FIELD,
    NOTE_FIELD,
    auth.signature
)


db.define_table(
    "staff",
    APP_FIELD,
    Field("first_name", requires=IS_NOT_EMPTY()),
    Field("last_name", requires=IS_NOT_EMPTY()),
    Field("role", requires=IS_IN_SET(
        ["MA", 'RN', 'BSN', "Office Manager", "Intern", "Phlebotomist", "Front Desk", "Other (describe in note)"],
        sort=True,
        zero=None)),
    DAYS_OF_WEEK_FIELD(label="Official days"),
    # Field("job_description", 'text', comment=XML("Enter a brief description of the <b>patient-centered</b>"
    #                                              " tasks this employee conducts <i>(i.e. tracks referrals, "
    #                                              "makes call-backs, etc.)</i>."),
    #      requires=IS_LENGTH(minsize=140, maxsize=1000)),
    NOTE_FIELD,
    format=staff_format
)

# 2D 1

db.define_table(
    'huddle_sheet',
    APP_FIELD,
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )


db.define_table(
    'meeting_sheet',
    APP_FIELD,
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )


db.define_table(
    'training_sheet',
    APP_FIELD,
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )

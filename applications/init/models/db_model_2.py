staff_format = '%(first_name)s %(last_name)s (%(role)s)'
db.define_table(
    "provider",
    Field("first_name", requires=IS_NOT_EMPTY()),
    Field("last_name", requires=IS_NOT_EMPTY()),
    Field("email", requires=IS_EMAIL()),
    Field("npi", label='NPI#'),  # requires=IS_NOT_EMPTY()),
    Field("dea", label='DEA#'),  # requires=IS_NOT_EMPTY()),
    Field("license", label='License #'),  # requires=IS_NOT_EMPTY()),
    Field("role", requires=IS_IN_SET(["MD", "DO", "APRN (i.e. NP)", "PA"], sort=True, zero=None)),
    Field("bills_under", 'list:reference provider', label='Bills Under / Shares Patients Under'),
    DAYS_OF_WEEK_FIELD(label="Official days",
                       comment="Only select the days when patients are seen by this provider in this location."),
    # Field("job_description", 'text', comment=XML("Enter a brief description of the <b>patient-centered</b>"
    #                                              " tasks this provider conducts <i>(i.e. tracks referrals, "
    #                                              "makes call-backs, etc.)</i> outside of an examination."),
    #      requires=IS_LENGTH(minsize=140, maxsize=1000)),
    
    format=staff_format,
    # auth.signature  # not needed because db._common_fields.append(auth.signature)
)

db.provider.bills_under.requires = IS_IN_DB(db(db.provider.application == APP_ID), 'provider.application',
                                            staff_format, multiple=True)


db.define_table(
    "other_staff",
    
    YES_NO_FIELD,
    
    auth.signature
)


db.define_table(
    "staff",
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
    
    format=staff_format
)

# 2D 1

db.define_table(
    'huddle_sheet',
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    
    )


db.define_table(
    'meeting_sheet',
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    
    )


db.define_table(
    'training_sheet',
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    
    )


db.define_table(
    'patient_population',
    Field('patients', requires=IS_INT_IN_RANGE(200, 20001)),
    )


db.define_table(
    'race',
    Field('native_american', label="Native American", requires=IS_INT_IN_RANGE(0, 101)),
    Field('pacific_islander', label="Pacific Islander", requires=IS_INT_IN_RANGE(0, 101)),
    Field('black', label="Black or African American", requires=IS_INT_IN_RANGE(0, 101)),
    Field('white', label="White or Caucasian", requires=IS_INT_IN_RANGE(0, 101)),
    Field('south_asian', label="South Asian", requires=IS_INT_IN_RANGE(0, 101)),
    Field('east_asian', label="East Asian", requires=IS_INT_IN_RANGE(0, 101)),
    Field('south_central_american', label="East Asian", requires=IS_INT_IN_RANGE(0, 101)),
    )


db.define_table(
    'ethnicity',
    Field('hispanic', requires=IS_INT_IN_RANGE(0, 101)),
    Field('non_hispanic', label="Non-Hispanic", requires=IS_INT_IN_RANGE(0, 101)),
    )


db.define_table(
    'languages',
    Field('english', requires=IS_INT_IN_RANGE(0, 101)),
    Field('spanish', requires=IS_INT_IN_RANGE(0, 101)),
    Field('chinese', requires=IS_INT_IN_RANGE(0, 101)),
    Field('hindi', requires=IS_INT_IN_RANGE(0, 101)),
    Field('bengali', requires=IS_INT_IN_RANGE(0, 101)),
    Field('arabic', requires=IS_INT_IN_RANGE(0, 101)),
    Field('african', requires=IS_INT_IN_RANGE(0, 101)),
    )


db.define_table(
    'gender',
    Field('male', requires=IS_INT_IN_RANGE(0, 101)),
    Field('female', requires=IS_INT_IN_RANGE(0, 101)),
    Field('other', requires=IS_INT_IN_RANGE(0, 101)),
    )

db.define_table(
    'meaningful_use_2014',
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
)

db.define_table(
    "patient_demographics",
    Field("please_choose", "list:string"
          # requires=IS_IN_SET([(0, 'Date of birth')...  # this is handled in corresponding controller
          ),
)

SERVICES = [("immunization", "vaccinations/immunizations"),
            ("preventative", "preventative"),
            ("chronic", "chronic/acute")]

for svc in SERVICES:
    db.define_table(
        'callback_list_%s' % svc[0],
        Field('choose_file', 'upload', uploadfield='file_data'),
        Field('file_data', 'blob'),
        Field('file_description', requires=IS_NOT_EMPTY()),
    )

db.define_table(
    "medical_history",

    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=DATE_VALIDATOR),
    Field("service_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    *SCREENSHOT_FIELDS
)

db.define_table(
    "family_history",

    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=DATE_VALIDATOR),
    Field("service_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    *SCREENSHOT_FIELDS
)
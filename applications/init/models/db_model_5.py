# (5A)###################################################


db.define_table('lab_tracking_generic',
                Field("application", 'reference application', readable=False, writable=False),
                Field('choose_file', 'upload', uploadfield='file_data'),
                Field('file_data', 'blob'),
                Field('file_description', requires=IS_NOT_EMPTY()),
                _note_field,
                )

db.define_table('lab_tracking_emr',
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )

db.define_table('image_tracking_generic',
                Field("application", 'reference application', readable=False, writable=False),
                Field('choose_file', 'upload', uploadfield='file_data'),
                Field('file_data', 'blob'),
                Field('file_description', requires=IS_NOT_EMPTY()),
                _note_field,
                )

db.define_table('image_tracking_emr',
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )

db.define_table('lab_image_follow_up',
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )

db.define_table('lab_image_follow_up_examples',
                Field("application", 'reference application', readable=False, writable=False),
                Field("patient_name", requires=IS_NOT_EMPTY()),
                Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
                _note_field,
                )

# (5B)###################################################


db.define_table('referral_blurb',
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )

db.define_table('referral_tracking_generic',
                Field("application", 'reference application', readable=False, writable=False),
                Field('choose_file', 'upload', uploadfield='file_data'),
                Field('file_data', 'blob'),
                Field('file_description', requires=IS_NOT_EMPTY()),
                _note_field,
                )

db.define_table('referral_tracking_emr',
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )

# (5C 1)###################################################


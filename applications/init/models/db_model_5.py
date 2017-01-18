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
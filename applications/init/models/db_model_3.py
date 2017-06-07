db.define_table('meaningful_use_2014',
                Field("application", 'reference application', readable=False, writable=False),
                Field('choose_file', 'upload', uploadfield='file_data'),
                Field('file_data', 'blob'),
                Field('file_description', requires=IS_NOT_EMPTY()),
                NOTE_FIELD,
                )

db.define_table("patient_demographics",
                Field("application", 'reference application', readable=False, writable=False),
                Field("please_choose", "list:string"
                     #requires=IS_IN_SET([(0, 'Date of birth')...  # this is handled in corresponding controller
                ),
                NOTE_FIELD,
                )


db.define_table('callback_list',
                APP_FIELD,
                Field('choose_file', 'upload', uploadfield='file_data'),
                Field('file_data', 'blob'),
                Field('file_description', requires=IS_NOT_EMPTY()),
                NOTE_FIELD,
                )

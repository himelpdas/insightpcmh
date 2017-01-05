db.define_table('meaningful_use_2014',
                Field("application", 'reference application', readable=False, writable=False),
                Field('choose_file', 'upload', uploadfield='file_data'),
                Field('file_data', 'blob'),
                Field('file_description', requires=IS_NOT_EMPTY()),
                _note_field,
                )
db.define_table('report_card',
                APP_FIELD,
                Field('choose_file', 'upload', uploadfield='file_data'),
                Field('file_data', 'blob'),
                Field('file_description', requires=IS_NOT_EMPTY()),
                NOTE_FIELD,
                )

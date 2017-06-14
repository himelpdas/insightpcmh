db.define_table(
    'report_card',
    
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    )

db.define_table(
    'award',
    YES_NO_FIELD,
    )

db.define_table(
    'award_document',
    
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    )

db.define_table(
    'report_card',
    APP_FIELD,
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )

db.define_table(
    'award',
    APP_FIELD,
    YES_NO_FIELD,
    NOTE_FIELD,
    )

db.define_table(
    'award_document',
    APP_FIELD,
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )

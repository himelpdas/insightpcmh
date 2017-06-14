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

db.define_table(
    'callback_list',
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
)

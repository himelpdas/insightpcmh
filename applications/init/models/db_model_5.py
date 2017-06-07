# (5A)###################################################

db.define_table(
    'lab_tracking',
    APP_FIELD, 
    YES_NO_FIELD,
    NOTE_FIELD,
    )

db.define_table(
    'lab_tracking_chart',
    APP_FIELD, 
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )

db.define_table(
    'image_tracking',
    APP_FIELD,
    YES_NO_FIELD,
    NOTE_FIELD,
    )

db.define_table(
    'image_tracking_chart',
    APP_FIELD, 
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )

db.define_table(
    'referral_tracking',
    APP_FIELD,
    YES_NO_FIELD,
    NOTE_FIELD,
    )

db.define_table(
    'referral_tracking_chart',
    APP_FIELD, 
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )

db.define_table(
    'lab_follow_up',
    APP_FIELD, 
    YES_NO_FIELD,
    NOTE_FIELD,
    )

db.define_table(
    'image_follow_up',
    APP_FIELD, 
    YES_NO_FIELD,
    NOTE_FIELD,
    )

db.define_table(
    'referral_follow_up',
    APP_FIELD, 
    YES_NO_FIELD,
    NOTE_FIELD,
    )

db.define_table(
    'lab_follow_up_normal_example',
    APP_FIELD, 
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
    NOTE_FIELD,
    )

db.define_table(
    'lab_follow_up_abnormal_example',
    APP_FIELD,
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
    NOTE_FIELD,
    )

db.define_table(
    'image_follow_up_normal_example',
    APP_FIELD, 
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
    NOTE_FIELD,
    )

db.define_table(
    'image_follow_up_abnormal_example',
    APP_FIELD,
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
    NOTE_FIELD,
    )

db.define_table(
    'referral_follow_up_normal_example',
    APP_FIELD, 
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
    NOTE_FIELD,
    )

db.define_table(
    'referral_follow_up_abnormal_example',
    APP_FIELD,
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
    NOTE_FIELD,
    )

# (5B)###################################################


db.define_table(
    'referral_blurb',
    APP_FIELD,
    YES_NO_FIELD,
    NOTE_FIELD,
    )

db.define_table(
    'specialist_order_example',
    APP_FIELD,
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )

db.define_table(
    'psych_order_example',
    APP_FIELD,
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )

# (5C)###################################################

db.define_table(
    'er_ip_log',
    APP_FIELD,
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    NOTE_FIELD,
    )

# (6A)###################################################


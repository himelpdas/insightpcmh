# (5A)###################################################

db.define_table(
    'lab_tracking',
     
    YES_NO_FIELD,
    
    )

db.define_table(
    'lab_tracking_chart',
     
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    
    )

db.define_table(
    'image_tracking',
    
    YES_NO_FIELD,
    
    )

db.define_table(
    'image_tracking_chart',
     
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    
    )

db.define_table(
    'referral_tracking',
    
    YES_NO_FIELD,
    
    )

db.define_table(
    'referral_tracking_chart',
     
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    
    )

db.define_table(
    'lab_follow_up',
     
    YES_NO_FIELD,
    
    )

db.define_table(
    'image_follow_up',
     
    YES_NO_FIELD,
    
    )

db.define_table(
    'referral_follow_up',
     
    YES_NO_FIELD,
    
    )

db.define_table(
    'developmental_screening',

    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=DATE_VALIDATOR),
    Field("service_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    *SCREENSHOT_FIELDS
)

db.define_table(
    'lab_follow_up_normal_example',
     
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=DATE_VALIDATOR),
    Field("service_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    *SCREENSHOT_FIELDS
    )

db.define_table(
    'lab_follow_up_abnormal_example',
    
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=DATE_VALIDATOR),
    Field("service_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    *SCREENSHOT_FIELDS
    )

db.define_table(
    'image_follow_up_normal_example',
     
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=DATE_VALIDATOR),
    Field("service_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    *SCREENSHOT_FIELDS
    )

db.define_table(
    'image_follow_up_abnormal_example',
    
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=DATE_VALIDATOR),
    Field("service_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    *SCREENSHOT_FIELDS
    )

db.define_table(
    'referral_follow_up_normal_example',
     
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=DATE_VALIDATOR),
    Field("service_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    *SCREENSHOT_FIELDS
    )

db.define_table(
    'referral_follow_up_abnormal_example',
    
    Field("patient_name", requires=IS_NOT_EMPTY()),
    Field("patient_dob", "date", label="Patient DOB", requires=DATE_VALIDATOR),
    Field("service_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    *SCREENSHOT_FIELDS
    )

# (5B)###################################################


db.define_table(
    'referral_blurb',
    
    YES_NO_FIELD,
    
    )

db.define_table(
    'specialist_order_example',
    
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    
    )

db.define_table(
    'psych_order_example',
    
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    
    )

# (5C)###################################################

db.define_table(
    'er_ip_log',
    
    Field('choose_file', 'upload', uploadfield='file_data'),
    Field('file_data', 'blob'),
    Field('file_description', requires=IS_NOT_EMPTY()),
    
    )

# (6A)###################################################


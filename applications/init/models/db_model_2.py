####Transition of Care Internal####
db.define_table("transition_of_care_plan_internal",
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field, auth.signature)

db.define_table("intake_form",
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field, auth.signature)

db.define_table("intake_form_upload",
                Field("application", 'reference application', readable=False, writable=False),
                Field("upload", "upload", requires=IS_NOT_EMPTY(), label="Upload Intake Form"),
                Field("filename", readable=False, writable=False),
                _note_field,
                 auth.signature)

db.define_table("intake_form_patient_example",
                Field("application", 'reference application', readable=False, writable=False),
                Field("patient_first_name", label="Patient First Name", requires=IS_NOT_EMPTY()),
                Field("patient_last_name", label="Patient Last Name", requires=IS_NOT_EMPTY()),
                Field("patient_DOB", "date", label="Patient DOB", requires=IS_NOT_EMPTY()),
                _note_field,
                auth.signature
)
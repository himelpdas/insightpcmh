db.define_table("pcmh_Primary_Contact",
Field("name"),
Field("email", requires=IS_EMAIL()),
Field("phone", requires=IS_MATCH("^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}$")),
Field("role", requires=IS_IN_SET(["MD", "PA", "MA", "Manager", "Other"], zero=None)),
Field("owner_email", requires=_telephone_field_validator),
)

####Transition of Care Internal####
db.define_table("transition_of_care_plan_internal",
                _yes_no_field_default,
                _note_field)

db.define_table("intake_form",
                _yes_no_field_default,
                _note_field)

db.define_table("intake_form_upload",
                Field("upload", "upload", label="Upload Intake Form"),
                Field("filename", readable=False, writable=False),
                _note_field)

db.define_table("intake_form_patient_example",
                Field("patient_1_first_name"),
                Field("patient_1_last_name"),
                Field("patient_1_DOB", "date", label="Patient 1 DOB"),
                Field("patient_2_first_name"),
                Field("patient_2_last_name"),
                Field("patient_2_DOB", "date", label="Patient 2 DOB"),
                Field("patient_3_first_name"),
                Field("patient_3_last_name"),
                Field("patient_3_DOB", "date", label="Patient 3 DOB"),)
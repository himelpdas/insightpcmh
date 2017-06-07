MEASURES_3E = [("mental_plan", "mental health disorder or substance use disorder"),
               ("chronic_plan", "chronic medical condition"),
               ("acute_plan", "acute condition"),
               ("unhealthy_plan", "unhealthy behaviors (i.e. smoking, poor diet, etc.)", "well/annual visit")]

db.define_table(
    'care_plan',
    APP_FIELD,
    YES_NO_FIELD,
    NOTE_FIELD,
    )

for _each in MEASURES_3E:
    db.define_table(
        _each[0],
        APP_FIELD,
        Field("patient_name", requires=IS_NOT_EMPTY()),
        Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
        Field("service_date", "date", label="Patient DOB", requires=IS_DATE()),
        NOTE_FIELD,
        )

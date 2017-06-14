MEASURES_3E = [("mental_plan", "mental health disorder or substance use disorder"),
               ("chronic_plan", "chronic medical condition"),
               ("acute_plan", "acute condition"),
               ("unhealthy_plan", "unhealthy behaviors (i.e. smoking, poor diet, etc.)", "well/annual visit")]

db.define_table(
    'care_plan',
    
    YES_NO_FIELD,
    
    )

for _each in MEASURES_3E:
    db.define_table(
        _each[0],
        
        Field("patient_name", requires=IS_NOT_EMPTY()),
        Field("patient_dob", "date", label="Patient DOB", requires=DATE_VALIDATOR),
        Field("service_date", "date", label="Service Date", requires=DATE_VALIDATOR),
        *SCREENSHOT_FIELDS
        )

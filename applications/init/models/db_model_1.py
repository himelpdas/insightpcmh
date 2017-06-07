db.define_table("office_hours",
    APP_FIELD,
    DAY_FIELD(),
    Field("start_time", "time", requires=_am_pm_time_validator, label="Opens"),
    Field("end_time", "time", requires=_am_pm_time_validator, label="Closes"),
    NOTE_FIELD,
    # auth.signature  # not needed because db._common_fields.append(auth.signature)
)

db.define_table("same_day_appointments",
                APP_FIELD,
                YES_NO_FIELD,
                NOTE_FIELD,
                )

db.define_table("same_day_block",
                APP_FIELD,
                DAY_FIELD(),
                Field("start_time", "time", requires=_am_pm_time_validator),
                # DO NOT use IS_NOT_EMPTY, as it will be submitted as a String instead of a datetime.time object!
                Field("end_time", "time", requires=_am_pm_time_validator),
                NOTE_FIELD,
                )

db.define_table("after_hours",
                APP_FIELD,
                YES_NO_FIELD,
                NOTE_FIELD,
                )

db.define_table("after_hour_block",
                APP_FIELD,
                DAY_FIELD(),
                Field("start_time", "time", requires=_am_pm_time_validator),
                # DO NOT use IS_NOT_EMPTY, as it will be submitted as a String instead of a datetime.time object!
                Field("end_time", "time", requires=_am_pm_time_validator),
                NOTE_FIELD,
                )

db.define_table("no_shows",
                APP_FIELD,
                Field("how_often", label="How Often?", requires=IS_IN_SET(
                    [(0, "We don't do it or don't know how"), (1, "About once a day"), (2, "About once a week"),
                     (3, "About once a month")])),
                NOTE_FIELD,
                )

db.define_table("walkin",
                APP_FIELD,
                YES_NO_FIELD,
                NOTE_FIELD,
                )

_unit_field = Field("unit", requires=IS_IN_SET(['Minutes', 'Hour(s)', 'Day(s)', 'Week(s)', 'Month(s)']))
db.define_table("next_available_appointment",
                APP_FIELD,
                Field("appointment_type"),
                Field("available_within", "integer"),
                _unit_field,
                NOTE_FIELD,
)

db.define_table(
    "no_show_emr",
    APP_FIELD,
    YES_NO_FIELD,
    NOTE_FIELD,
)

# (availability of appointments)###################################################

_within = IS_IN_SET([(0, "Same Day"), (1, "1 Day"), (2, "2 Days"), (3, "3 Days"), (4, "4 Days"), (5, "5 Days"),
                     (6, "6 Days"), (7, "7 Days (1 Week)"), (10, "1.5 Weeks"), (14, "2 Weeks"),
                     (21, "3 Weeks")], zero=None)
db.define_table(
    "availability_of_appointments",
    APP_FIELD,
    Field("new_patient", requires=_within),
    Field("urgent", requires=_within),
    Field("consult", requires=_within),
    Field("walk_in", requires=_within),
    Field("same_day", requires=_within),
    NOTE_FIELD,
    auth.signature
)

# (1B)###################################################

db.define_table("answering_service",
                APP_FIELD,
                Field("please_choose", requires=IS_IN_SET(["Answering service", "Call forwarding to provider"], zero=None)),
                NOTE_FIELD,
                )


db.define_table("telephone_encounter",
                APP_FIELD,
                YES_NO_FIELD,
                NOTE_FIELD,
                )

db.define_table('telephone_encounter_during_hours_example',
                APP_FIELD,
                Field("patient_name", requires=IS_NOT_EMPTY()),
                Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
                NOTE_FIELD,
                )

db.define_table('telephone_encounter_after_hours_example',
                APP_FIELD,
                Field("patient_name", requires=IS_NOT_EMPTY()),
                Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
                NOTE_FIELD,
                )


db.define_table('telephone_encounter_log',
                APP_FIELD,
                Field('choose_file', 'upload', uploadfield='file_data'),
                Field('file_data', 'blob'),
                Field('file_description', requires=IS_NOT_EMPTY()),
                NOTE_FIELD,
                )

# (1C)###################################################

db.define_table('meaningful_use',
                APP_FIELD,
                Field('choose_file', 'upload', uploadfield='file_data'),
                Field('file_data', 'blob'),
                Field('file_description', requires=IS_NOT_EMPTY()),
                NOTE_FIELD,
                )
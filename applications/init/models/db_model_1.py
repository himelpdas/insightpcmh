db.define_table("same_day_appointments",
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )

db.define_table("same_day_block",
                Field("application", 'reference application', readable=False, writable=False),
                _day_of_week_field(),
                Field("start_time", "time", requires=_am_pm_time_validator),
                # DO NOT use IS_NOT_EMPTY, as it will be submitted as a String instead of a datetime.time object!
                Field("end_time", "time", requires=_am_pm_time_validator),
                _note_field,
                )

db.define_table("after_hours",
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )

db.define_table("after_hour_block",
                Field("application", 'reference application', readable=False, writable=False),
                _day_of_week_field(),
                Field("start_time", "time", requires=_am_pm_time_validator),
                # DO NOT use IS_NOT_EMPTY, as it will be submitted as a String instead of a datetime.time object!
                Field("end_time", "time", requires=_am_pm_time_validator),
                _note_field,
                )

db.define_table("no_shows",
                Field("application", 'reference application', readable=False, writable=False),
                Field("how_often", label="How Often?", requires=IS_IN_SET(
                    [(0, "We don't do it or don't know how"), (1, "About once a day"), (2, "About once a week"),
                     (3, "About once a month")])),
                _note_field,
                )

db.define_table("walkin",
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )

_unit_field = Field("unit", requires=IS_IN_SET(['Minutes', 'Hour(s)', 'Day(s)', 'Week(s)', 'Month(s)']))
db.define_table("next_available_appointment",
                Field("application", 'reference application', readable=False, writable=False),
                Field("appointment_type"),
                Field("available_within", "integer"),
                _unit_field,
                _note_field,
)

db.define_table("no_show_emr",
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )

# (1B)###################################################

db.define_table("answering_service",
                Field("application", 'reference application', readable=False, writable=False),
                Field("please_choose", requires=IS_IN_SET(["Answering service", "Call forwarding to provider"], zero=None)),
                _note_field,
                )


db.define_table("telephone_encounter",
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )

db.define_table('telephone_encounter_examples',
                Field("application", 'reference application', readable=False, writable=False),
                Field("patient_name", requires=IS_NOT_EMPTY()),
                Field("patient_dob", "date", label="Patient DOB", requires=IS_DATE()),
                _note_field,
                )

# (1C)###################################################

db.define_table('meaningful_use',
                Field("application", 'reference application', readable=False, writable=False),
                Field('choose_file', 'upload', uploadfield='file_data'),
                Field('file_data', 'blob'),
                Field('file_description', requires=IS_NOT_EMPTY()),
                _note_field,
                )
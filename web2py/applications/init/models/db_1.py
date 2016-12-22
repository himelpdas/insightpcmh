db.define_table("same_day_appointments",
                _yes_no_field_default,
                _note_field,
                )

db.define_table("same_day_block",
                _day_of_week_field(),
                Field("start_time", "time", requires=_am_pm_time_validator),
                # DO NOT use IS_NOT_EMPTY, as it will be submitted as a String instead of a datetime.time object!
                Field("end_time", "time", requires=_am_pm_time_validator),
                _note_field,
                )

db.define_table("after_hours",
                _yes_no_field_default,
                _note_field,
                )

db.define_table("after_hour_block",
                _day_of_week_field(),
                Field("start_time", "time", requires=_am_pm_time_validator),
                # DO NOT use IS_NOT_EMPTY, as it will be submitted as a String instead of a datetime.time object!
                Field("end_time", "time", requires=_am_pm_time_validator),
                _note_field,
                )

db.define_table("no_shows",
                Field("how_often", label="How Often?", requires=IS_IN_SET(
                    [(0, "We don't do it or don't know how"), (1, "About once a day"), (2, "About once a week"),
                     (3, "About once a month")])),
                _note_field,
                )

db.define_table("walkin",
                _yes_no_field_default,
                _note_field,
                )

_unit_field = Field("unit", requires=IS_IN_SET(['Minutes', 'Hour(s)', 'Day(s)', 'Week(s)', 'Month(s)']))
db.define_table("next_available_appointment",
                Field("appointment_type"),
                Field("available_within", "integer"),
                _unit_field,
                _note_field,
                )

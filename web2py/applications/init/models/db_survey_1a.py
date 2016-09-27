db.define_table("same_day_appointments",
    _yes_no_field_default,
    _note_field
)

db.define_table("same_day_block",
    _day_of_week_field(),
    Field("start_time", "time", requires=_am_pm_time_validator),  # DO NOT use IS_NOT_EMPTY, as it will be submitted as a String instead of a datetime.time object!
    Field("end_time", "time", requires=_am_pm_time_validator),
    _note_field
)

db.define_table("after_hours",
    _yes_no_field_default,
    _note_field
)

db.define_table("after_hour_block",
    _day_of_week_field(),
    Field("start_time", "time", requires=_am_pm_time_validator),  # DO NOT use IS_NOT_EMPTY, as it will be submitted as a String instead of a datetime.time object!
    Field("end_time", "time", requires=_am_pm_time_validator),
    _note_field
)

db.define_table("no_shows",
    Field("how_often", label="How Often?", requires=IS_IN_SET([(0, "We don't do it or don't know how"),  (1, "About once a day"), (2, "About once a week"),  (3, "About once a month")])),
    _note_field
)

db.define_table("walkin",
    _yes_no_field_default,
    _note_field
)

db.define_table("next_available_appointment",
    _day_of_week_field(),
    Field("appointment_type"),
    Field("available_within", "integer"),
    Field("unit", requires=IS_IN_SET([("m", "Minutes"), ("h", "Hour(s)"), ("d", "Day(s)"), ("w", "Week(s)")])),
    _note_field
)
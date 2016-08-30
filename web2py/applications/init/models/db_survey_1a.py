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
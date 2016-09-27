db.define_table("pcmh_primary_contact",
Field("name"),
Field("email", requires=IS_EMAIL()),
Field("phone", requires=IS_MATCH("^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}$")),
Field("role", requires=IS_IN_SET(["MD", "PA", "MA", "Manager", "Other"], zero=None)),
Field("owner_email", requires=_telephone_field_validator),
_note_field,
)

db.define_table("clinical_hours",
_day_of_week_field(),
Field("start_time", "time", label="Opens"),
Field("end_time", "time", label="Closes"),
_note_field,
)
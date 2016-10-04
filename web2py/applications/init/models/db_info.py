_list_of_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

db.define_table("practice_info",
Field("practice_name", requires=IS_NOT_EMPTY()),
Field("practice_specialty", requires=IS_IN_SET(['Internal Medicine', 'Pediatrics', 'Family Medicine'], sort=True, zero=None)),
Field("phone", requires=_telephone_field_validator),
Field("extension", requires=IS_EMPTY_OR(_IS_DIGITS()), comment="Optional"),
Field("address_line_1", requires=IS_NOT_EMPTY()),
Field("address_line_2", comment="Optional"),
Field("city", requires=IS_NOT_EMPTY()),
Field("state_", label="State", requires=IS_IN_SET(_list_of_states, zero=None)),
Field("website", requires=IS_EMPTY_OR(IS_URL()), comment="Optional"),
_note_field,
)

_practice = db(db.practice_info.id > 0).select().last() or Storage(practice_name="The practice")

db.define_table("primary_contact",
Field("first_name", requires=IS_NOT_EMPTY()),
Field("last_name", requires=IS_NOT_EMPTY()),
Field("email", requires=IS_EMAIL()),
Field("phone", requires=IS_EMPTY_OR(_telephone_field_validator), comment="Leave blank if same as practice number"),
Field("extension", requires=IS_EMPTY_OR(_IS_DIGITS()), comment="Optional"),
Field("role", requires=IS_IN_SET(["MD", "PA", "MA", "Manager", "Other"], sort=True, zero=None)),
_note_field,
)

db.define_table("clinical_hour",
_day_of_week_field(),
Field("start_time", "time", label="Opens"),
Field("end_time", "time", label="Closes"),
_note_field,
)

db.define_table("provider",
Field("first_name", requires=IS_NOT_EMPTY()),
Field("last_name", requires=IS_NOT_EMPTY()),
Field("email", requires=IS_EMAIL()),
Field("role", requires=IS_IN_SET(["MD", "DO", "NP", "PA"], sort=True, zero=None)),
Field("is_billing_provider", 'boolean', comment=""),
_days_of_week_field(label="Typical days", comment="Select the days when patients are usually seen by this provider"),
_note_field,
)

db.define_table("has_non_provider",
    _yes_no_field_default,
    _note_field
)

db.define_table("non_provider",
Field("first_name", requires=IS_NOT_EMPTY()),
Field("last_name", requires=IS_NOT_EMPTY()),
Field("role", requires=IS_IN_SET(sorted(["MA", "Manager", "Intern", "Phlebotomist", "Front Desk", "Other (leave note)"]), zero=None)),
_days_of_week_field(label="Typical days", comment="Select the days when this non-provider is usually at the office"),
_note_field,
)
"""
db.define_table("training_log",
    Field("practice", requires=IS_NOT_EMPTY()),
    Field("owner_id", db.auth_user, label="Primary Contact"),
)
"""
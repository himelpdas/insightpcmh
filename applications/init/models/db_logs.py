db.define_table("logging",
    Field("owner_id", db.auth_user, label="Author"),
    Field("application", db.application),
    Field("description", 'text'),
    Field("difficulty", requires=IS_IN_SET(["High", "Medium", "Low"], zero=None)),
)

db.logging.application.widget = SQLFORM.widgets.autocomplete(
    request, db.application.practice_name, limitby=(0, 10), min_length=0, distinct=True,
    id_field=db.application.id)
db.define_table("logging",
    Field("owner_id", db.auth_user, label="Author"),
    Field("description", 'text', requires=IS_NOT_EMPTY()),
    Field("people_involved", 'list:string', requires=IS_NOT_EMPTY()),
    Field("difficulty", requires=IS_IN_SET(["High", "Medium", "Low", "No Issue/Resolved"], zero=None)),
)

db.logging.application.widget = SQLFORM.widgets.autocomplete(
    request, db.application.practice_name, limitby=(0, 10), min_length=0, distinct=True,
    id_field=db.application.id)

db.logging._enable_record_versioning()
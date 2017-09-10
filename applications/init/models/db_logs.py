db.define_table(
    "logging",
    Field("owner_id", db.auth_user, label="Author"),
    Field("people_involved", 'list:string', requires=IS_NOT_EMPTY()),
    Field("contact_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    Field("start_time", "time", requires=AM_PM_VALIDATOR),
    Field("end_time", "time", requires=AM_PM_VALIDATOR),
    Field("contact_type", requires=IS_IN_SET(["Meeting", "Telephone", "Email", "SMS"], zero=None)),
    Field("problem_or_canceled", "boolean"),
    Field("goals_met", 'text', requires=IS_NOT_EMPTY()),
    Field("goals_not_met", 'text', requires=IS_NOT_EMPTY()),
    Field("follow_up_date", "date", label="Service Date", requires=DATE_VALIDATOR),
    Field("follow_up_time", "time", requires=AM_PM_VALIDATOR),
)

db.logging.application.widget = SQLFORM.widgets.autocomplete(
    request, db.application.practice_name, limitby=(0, 10), min_length=0, distinct=True,
    id_field=db.application.id)

db.logging._enable_record_versioning()
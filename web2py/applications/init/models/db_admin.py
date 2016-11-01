db.define_table("application",
    Field("owner_id", db.auth_user),
    Field('pps', label="PPS"),
    Field("application_type", requires=IS_IN_SET(["New", "Renewal"])),
    Field("application_size", requires=IS_IN_SET(["Single", "Corporate"]), comment='Choose "Corporate" if there are 3 or more sites under one owner or CEO. Otherwise the application should be treated as "Single."'),
    Field('corporate_name', requires=IS_NOT_EMPTY() if request.vars.application_size == "Multi" else None),
    Field('largest_practice', 'boolean', comment="Is this the practice with the most active lives?",
          label="Is Largest Practice?", requires=IS_NOT_EMPTY() if request.vars.application_size == "Multi" else None),
    Field("website", requires=IS_EMPTY_OR(IS_URL()), comment="Optional"),
    #
    Field("practice_name", requires=IS_NOT_EMPTY()),
    Field("practice_specialty",
          requires=IS_IN_SET(['Internal Medicine', 'Pediatrics', 'Family Medicine'], sort=True, zero=None)),
    Field("practice_phone", requires=_telephone_field_validator),
    Field("practice_phone_extension", requires=IS_EMPTY_OR(_IS_DIGITS()), comment="Optional"),
    Field("practice_fax", requires=_telephone_field_validator),
    Field("practice_address_line_1", requires=IS_NOT_EMPTY()),
    Field("practice_address_line_2", comment="Optional"),
    Field("practice_city", requires=IS_NOT_EMPTY()),
    Field("practice_state", requires=IS_IN_SET(_list_of_states, zero=None))
)

db.application.pps.widget = SQLFORM.widgets.autocomplete(
    request, db.auth_user.pps, limitby=(0, 10), min_length=0)
db.application.corporate_name.widget = SQLFORM.widgets.autocomplete(
    request, db.auth_user.corporate_name, limitby=(0, 10), min_length=0)

_application_id = db(db.application.id == request.vars["application_id"]).select.last()

def initialize_app(form):
    if not auth.user.is_insight:
        application = db(db.application.owner_id == auth.user).select().last()
        if not application:
            redirect(URL('application'))

auth.settings.login_onvalidation.append(initialize_app)
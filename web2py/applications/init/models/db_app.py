EMRS = [('ecw','eClinicalWorks'), ('mdland', 'MDLand'), ('healthfusion','HealthFusion'), ('generic','Other')]

db.define_table("application",
    Field("owner_id", db.auth_user, required=True, default=auth.user.id if auth.user else None,
          writable=False, readable=False),
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
    Field("practice_zip", requires=IS_NOT_EMPTY()),
    Field("practice_state", requires=IS_IN_SET(_list_of_states, zero=None)),
    Field("practice_emr", label="Practice EMR", requires=IS_IN_SET(EMRS, sort=True, zero=None)),
)

db.application.pps.widget = SQLFORM.widgets.autocomplete(
    request, db.application.pps, limitby=(0, 10), min_length=0, distinct=True)  # http://bit.ly/2ex3oxE
db.application.corporate_name.widget = SQLFORM.widgets.autocomplete(
    request, db.application.corporate_name, limitby=(0, 10), min_length=0, distinct=True)

#_application_id = db(db.application.id == request.vars["application_id"]).select.last()


def _initialize_app(form):
    if not form.vars.is_insight:
        application = db(db.application.owner_id == auth.user).select().last()
        if not application:
            redirect(URL('new_application'))

auth.settings.login_onaccept.append(_initialize_app)
auth.settings.register_onaccept.append(_initialize_app)

MY_KEY="Himel"

if not auth.id_group("admins"):
    auth.add_group("admins", "Handles assigning trainers and app managers to applications. Automatically should given"
                      "membership to all applications")

if not auth.id_group("trainers"):
    auth.add_group("trainers", "Handles many applications. Has some additional responsibilites from app managers")

if not auth.id_group("app_managers"):
    auth.add_group("app_managers", "Handles data gathering.")


#IS_NOT_STAFF = not auth.has_membership(user_id=getattr(auth.user, "id", None), role="trainers") and \
#not auth.has_membership(user_id=getattr(auth.user, "id", None), role="admins")

IS_STAFF = bool(getattr(auth.user, "is_insight", None))

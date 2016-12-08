EMRS = [('#ecw', 'eClinicalWorks'), ('#mdland', 'MDLand'), ('#healthfusion', 'HealthFusion'), ('#generic', 'Other')]

db.define_table("application",
    Field("practice_name", requires=IS_NOT_EMPTY()),
    Field("owner_id", db.auth_user, label="Primary Contact", required=True, default=auth.user.id if auth.user else None,
          writable=False, readable=False),
    Field('pps', label="PPS"),
    Field("application_type", requires=IS_IN_SET(["Initial", "Renewal"])),
    Field("application_size", requires=IS_IN_SET(["Single", "Corporate"]), comment='Choose "Corporate" if there are 3 or more sites under one owner or CEO. Otherwise the application should be treated as "Single."'),
    Field('corporate_name', requires=IS_NOT_EMPTY() if request.vars.application_size == "Multi" else None),
    Field('largest_practice', 'boolean', comment="Is this the practice with the most active lives?",
          label="Largest Practice?", requires=IS_NOT_EMPTY() if request.vars.application_size == "Multi" else None),
    Field("emr", label="Primary EMR", requires=IS_IN_SET(EMRS, sort=True, zero=None)),
    Field("other_software", label="Secondary Software", comment=XML("If you use more than one software to run your practice, enter the name of the software here, otherwise <b>leave blank</b>. For example, some practices use a 2nd EMR as a scheduler or has a separate software for billing.")),
    Field("practice_specialty", label="Speciality",
          requires=IS_IN_SET(['Internal Medicine', 'Pediatrics', 'Family Medicine'], sort=True, zero=None)),
    Field("practice_phone", label="Phone", requires=_telephone_field_validator),
    Field("practice_phone_extension", label="Ext.", requires=IS_EMPTY_OR(_IS_DIGITS()), comment="Optional"),
    Field("practice_fax", label="Fax", requires=_telephone_field_validator),
    Field("practice_address_line_1", label="Address Line 1",requires=IS_NOT_EMPTY()),
    Field("practice_address_line_2", label="Line 2", comment="Optional"),
    Field("practice_city", label="City", requires=IS_NOT_EMPTY()),
    Field("practice_zip", label="Zip", requires=IS_NOT_EMPTY()),
    Field("practice_state", label="State", requires=IS_IN_SET(_list_of_states, zero=None)),
    Field("website", requires=IS_EMPTY_OR(IS_URL()), comment="Optional"),
    auth.signature
)

db.application.owner_id.widget = SQLFORM.widgets.autocomplete(
    request, db.auth_user.email, limitby=(0, 10), min_length=0, distinct=True,
    id_field=db.auth_user.id
)  # http://bit.ly/2ex3oxE
db.application.pps.widget = SQLFORM.widgets.autocomplete(
    request, db.application.pps, limitby=(0, 10), min_length=0, distinct=True)  # http://bit.ly/2ex3oxE
db.application.corporate_name.widget = SQLFORM.widgets.autocomplete(
    request, db.application.corporate_name, limitby=(0, 10), min_length=0, distinct=True)

#_application_id = db(db.application.id == request.vars["application_id"]).select.last()


#def _initialize_app(form):
#    if not form.vars.is_insight:
#        application = db(db.application.owner_id == auth.user).select().last()
#        if not application:
#            redirect(URL('new_application'))

#auth.settings.login_onaccept.append(_initialize_app)
#auth.settings.register_onaccept.append(_initialize_app)

MY_KEY="Himel"
if not session.MY_SALT:
    session.MY_SALT = os.urandom(8)

if not auth.id_group("admins"):
    auth.add_group("admins", "Handles assigning trainers and app managers to applications. Automatically should given"
                      "membership to all applications")

if not auth.id_group("trainers"):
    auth.add_group("trainers", "Handles many applications. Has some additional responsibilites from app managers")

if not auth.id_group("masters"):
    auth.add_group("masters", "Like admin, but bypasses permission")

if not auth.id_group("contributors"):
    auth.add_group("contributors", "The employees of a clinic that represent its corresponding application")

if not auth.id_group("app_managers"):
    auth.add_group("app_managers", "Handles data gathering")

if auth.is_logged_in():
    """Himel's role in Insight"""
    if auth.user.email in ["himel@insightmanagement.org", "himeldas@live.com"]:  # "jason@insightmanagement.org"]:
        for _role in {"masters", "admins", "trainers", "app_managers"}.symmetric_difference(auth.user_groups.values()):
            auth.add_membership(role=_role, user_id=auth.user.id)
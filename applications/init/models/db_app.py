db.define_table("application",
    Field("practice_name", requires=IS_NOT_EMPTY()),
    Field("owner_id", db.auth_user, comment="Enter primary contact's email address", label="Primary Contact", required=True, writable=False, readable=False),
    # Field("status", requires=IS_IN_SET(["1st Training Complete", "2nd Training Complete", "3rd Training Complete",
    #                                     "4th Training Complete", "Ready for Application Manager",
    #                                     "Working on Application", "Awaiting Documents from Practice"
    #                                     "Submitted", "OIF", "Add On",
    #                                     "Certified"], zero=None)),
    Field('pps', label="PPS"),
    Field("application_type", requires=IS_IN_SET(["Initial", "Renewal"])),
    Field("application_size", requires=IS_IN_SET(["Single", "Corporate"]),
          comment=XML('Choose "Corporate" if there are <b>3 or more</b> sites that can be represented by <b>one</b> '
                      'authorized representative (i.e. an owner or CEO). '
                      'Otherwise the application should be treated as "Single."')),
    Field('authorized_representative', label=SPAN("Authorized Representative (Email)",
                                                  _title="Applies to corporate tool only"),
          requires=IS_EMAIL() if request.post_vars.application_size == "Multi" else None),
    Field('largest_practice', 'boolean', default=True, comment="Is this the practice with the most active lives?",
          label=SPAN("Largest Site?", _title="Applies to corporate tool only"),
          requires=IS_NOT_EMPTY() if request.post_vars.application_size == "Multi" else None),
    Field("emr", label="Primary EMR", requires=IS_IN_SET(EMRS, sort=True, zero=None)),
    Field("other_software", label="Secondary Software", comment=XML("If you use more than one software to run your "
                                                                    "practice, enter the name of the software here, "
                                                                    "otherwise <b>leave blank</b>. For example, some "
                                                                    "practices use a 2nd EMR as a scheduler or has a "
                                                                    "separate software for billing.")),
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
    common_filter=lambda query: db.application.is_active==True,
    format='%(practice_name)s (%(id)s)'
    # auth.signature  # not needed because db._common_fields.append(auth.signature)
)

db.application.owner_id.widget = SQLFORM.widgets.autocomplete(
    request, db.auth_user.email, limitby=(0, 10), min_length=0, distinct=True,
    id_field=db.auth_user.id
)  # http://bit.ly/2ex3oxE
db.application.pps.widget = SQLFORM.widgets.autocomplete(
    request, db.application.pps, limitby=(0, 10), min_length=0, distinct=True)  # http://bit.ly/2ex3oxE
db.application.authorized_representative.widget = SQLFORM.widgets.autocomplete(
    request, db.application.authorized_representative, limitby=(0, 10), min_length=0, distinct=True)

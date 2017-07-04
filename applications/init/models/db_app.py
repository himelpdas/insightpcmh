db.define_table("application",
    Field("practice_name", requires=IS_NOT_EMPTY()),
    Field("first_site", 'boolean', label="First/Only site",
          comment=XML("Un-check this <u>only</u> if you or your parent company already "
                      "has other site(s) doing PCMH with us."), default=True),
    Field("progress", 'double', label="Data Progress", default=0.0, writable=False,
          represent=lambda value, row: '{:.1%}'.format(value)),
    Field("status", default="New",
          requires=IS_IN_SET(["New", "Gap Analysis", "Training", "Documenting", "Reviewing", "Submitted", "Under Audit",
                              "Scoring Stage 1", "Scoring Stage 2", "Scoring Stage 3", "Scoring Stage 4",
                              "Add On", "OIF", "Certified", "Practice Problem"],
                             zero=None)
          ),
    Field("certified_on", "date", writable=False, requires=DATE_VALIDATOR),
    Field("owner_id", db.auth_user, comment="Enter primary contact's email address.", label="Primary Contact", required=True, writable=False, readable=False),
    # Field("status", requires=IS_IN_SET(["1st Training Complete", "2nd Training Complete", "3rd Training Complete",
    #                                     "4th Training Complete", "Ready for Application Manager",
    #                                     "Working on Application", "Awaiting Documents from Practice"
    #                                     "Submitted", "OIF", "Add On",
    #                                     "Certified"], zero=None)),
    Field('pps', label="PPS"),
    Field("application_type", requires=IS_IN_SET(["Initial", "Renewal"])),
    # Field("application_size", requires=IS_IN_SET(["Single", "Corporate"]),
    #       comment=XML('Choose "Corporate" if there are <b>3 or more</b> sites that can be represented by <b>one</b> '
    #                   'authorized representative (i.e. an owner or CEO). '
    #                   'Otherwise the application should be treated as "Single."')),
    # Field('authorized_representative', label=SPAN("Authorized Representative (Email)",
    #                                               _title="Applies to corporate tool only"),
    #       requires=IS_EMAIL() if request.post_vars.application_size == "Multi" else None),
    # Field('largest_practice', 'boolean', default=True, comment="Is this the practice with the most active lives?",
    #      label=SPAN("Largest Site?", _title="Applies to corporate tool only"),
    #      requires=IS_NOT_EMPTY() if request.post_vars.application_size == "Multi" else None),
    Field("emr", label="Primary EMR", requires=IS_IN_SET(EMRS, sort=True, zero=None)),
    Field("other_software", label="Secondary Software", default="None",
          comment=XML("If you use more than one software to run your "
                      "practice, enter the name of the software here, "
                      "otherwise <b>leave blank</b>. For example, some "
                      "practices use a 2nd EMR as a scheduler or has a "
                      "separate software for billing.")),
    Field("practice_specialty", label="Speciality",
          requires=IS_IN_SET(['Internal Medicine', 'Pediatrics', 'Family Medicine'], sort=True, zero=None)),
    Field("practice_phone", label="Phone", requires=PHONE_VALIDATOR),
    Field("practice_phone_extension", label="Ext.", requires=IS_EMPTY_OR(IS_DIGITS()), comment="Optional"),
    Field("practice_fax", label="Fax", requires=PHONE_VALIDATOR),
    Field("practice_address_line_1", label="Address Line 1",requires=IS_NOT_EMPTY()),
    Field("practice_address_line_2", label="Line 2", comment="Optional"),
    Field("practice_city", label="City", requires=IS_NOT_EMPTY()),
    Field("practice_zip", label="Zip", requires=IS_NOT_EMPTY()),
    Field("practice_state", label="State", requires=IS_IN_SET(LIST_OF_STATES, zero=None)),
    Field("website", requires=IS_EMPTY_OR(IS_URL()), comment="Optional"),

    Field("force_complete", "list:string", readable=False, writable=False, default=[]),

    Field('practice_photo', 'upload', requires=IS_IMAGE(),
          uploadfield='file_data', readable=False, writable=False),
    Field('file_data', 'blob', readable=False, writable=False),

    common_filter=lambda query: db.application.is_active == True,
    format='%(practice_name)s (%(id)s)'
    # auth.signature  # not needed because db._common_fields.append(auth.signature)
)

db.application.emr_std = Field.Method(lambda row, emr=None:
                                      (emr if emr else row.application.emr).replace(" ", "_").lower())

db.application.owner_id.widget = SQLFORM.widgets.autocomplete(
    request, db.auth_user.email, limitby=(0, 10), min_length=0, distinct=True,
    id_field=db.auth_user.id
)  # http://bit.ly/2ex3oxE
db.application.pps.widget = SQLFORM.widgets.autocomplete(
    request, db.application.pps, limitby=(0, 10), min_length=0, distinct=True)  # http://bit.ly/2ex3oxE
# db.application.authorized_representative.widget = SQLFORM.widgets.autocomplete(
#     request, db.application.authorized_representative, limitby=(0, 10), min_length=0, distinct=True)
# db.application.linked_application.requires = IS_IN_DB(db, db.application, '%(practice_name)s (%(id)s)', multiple=True)


def PARTICIPATORS(row):
    return db(
        # JOIN SECTION
        (db.auth_group.id == db.auth_membership.group_id) &  # join auth_group and auth_membership
        (db.auth_user.id == db.auth_membership.user_id) &  # join auth_user and auth_membership
        (db.auth_permission.group_id == db.auth_group.id) &  # join auth_permission and auth_group
        # FILTER SECTION
        (db.auth_permission.record_id == row.id) &  # only where permission is given to this record
        (db.auth_permission.table_name == "application") &
        (db.auth_permission.name.belongs("manage", "train", "contribute"))  # trainers app mgrs and users
    ).select()

APP_FIELD = Field("application", 'reference application', readable=False, writable=False)

db._common_fields.append(APP_FIELD)
db._common_fields.append(NOTE_FIELD)

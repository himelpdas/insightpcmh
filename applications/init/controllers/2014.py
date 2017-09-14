# -*- coding: utf-8 -*-

"""
practice_info = MultiQNA(
    1,1,
    True,
    'practice_info',
    "Enter the information about your practice here."
)

practice_info.set_template("Practice: {practice_name} ({practice_specialty})<br>Phone: {phone} {extension}"
                           "<br>Address 1: {address_line_1}<br>Address 2: {address_line_2}<br>City: {city}<br>"
                           "State: {state_}<br>Web: {website}")

...
account_created.add_warning(getattr(account_created.row, "please_choose", None) == "No",
                            XML(T(
                                "Please create provide an account that has provider or admin level access, then "
                                "come back and change your answer.")))
"""

response.view = os.path.join("templates", "survey_2014.html")
# http://stackoverflow.com/questions/8750723/is-it-possible-to-change-a-web2py-view-on-the-fly


class Navigator:
    titles = ["Basic", "Access", "Team", "Population", "Care", "Coordination", "Performance"]

    def __init__(self):
        self.numerator = 0.0
        self.all_questions = List()
        # warning!! - function names MUST be sorted for init_list to work
        self.all_funcs = sorted(filter(lambda g: "pcmh_" == g[:5], globals()), key=lambda e: e.split("_", 2)[1])
        self.init_list()
        self.denominator = float(len(self.all_funcs))
        logger.info("Progress - num: %s den: %s" % (self.numerator, self.denominator))
        self.init_menu()
        self.init_title()

        progress = 1.0 if APP.status == "Certified" else self.numerator/self.denominator
        db(db.application.id == APP_ID).update(progress=progress)

    def init_title(self):
        if self.get_pcmh_from_request():
            pcmh = self.get_pcmh_from_request()
            label = self[pcmh]['elements'][self.get_element_from_request()]["label"]
            response.title = "PCMH ({pcmh}) {title} - {label}".format(
                pcmh=pcmh,
                title=self.get_title_from_pcmh(pcmh),
                label=label)

    def __getitem__(self, item):
        return self.all_questions[int(item)]

    @classmethod
    def get_title_from_pcmh(cls, pcmh):
        return cls.titles[int(cls.get_pcmh_from_request())]

    @classmethod
    def request_has_pcmh(cls, pcmh):
        return str(pcmh) == cls.get_pcmh_from_request()

    @classmethod
    def request_has_element(cls, element):
        return str(element) == cls.get_element_from_request()

    @staticmethod
    def get_pcmh_from_request():
        return List(request.function.split("_", 2))(1)

    @staticmethod
    def get_element_from_request():
        return List(request.function.split("_", 2))(2)  # warning! very important to split only twice

    def init_menu(self):
        for each in self.all_questions:
            response.menu.append(
                (
                    SPAN(SPAN(_class="glyphicon glyphicon-%s text-%s" %
                                     ("ok" if all(each.booleans) else "remove",
                                      "success" if all(each.booleans) else "danger")
                              ),
                         " (%s) " % each.pcmh, each.title),
                    self.request_has_pcmh(each.pcmh),  # get element 1 without error
                    each.index, []
                )
            )

    def function_is_complete(self, func):
        func()
        result = True
        for q in QNA.instances:
            if not q.table_name in APP.force_complete:
                if q.has_warnings() or q.needs_answer():
                    result = False
                    break
        if result:
            self.numerator += 1.0
        QNA.instances = []
        return result

    def init_list(self):
        """dynamically extracts the info from the function itself, rather than
        having to define it separately and add/remove the function accordingly"""
        for func_name in self.all_funcs:
            func = globals()[func_name]
            func_name_split = List(func_name.split("_", 2))
            func_name_header = func_name_split(0)
            if func_name_header == "pcmh":
                pcmh = int(func_name_split[1])
                element = func_name_split[2]

                assert func.__doc__, "missing doc strings for function %s" % func_name

                plural = " Elements " if element.count("__") > 1 else " Element "

                label = element.capitalize().replace("___", " | ").replace("__", ": ").replace("_", "/")

                is_complete = self.function_is_complete(func)
                icon = SPAN(_class="glyphicon glyphicon-%s text-%s" %
                                   ("ok" if is_complete else "remove",
                                    "success" if is_complete else "danger")
                            )

                description = SPAN(icon, " ", func.__doc__) if pcmh == 0 else \
                    SPAN(icon, plural, label, " → ", func.__doc__)

                pcmh_dict = self.all_questions(pcmh)

                if not pcmh_dict:
                    pcmh_dict = Storage(pcmh=pcmh, done=False, index=URL('2014', func_name, vars=request.get_vars))
                    pcmh_dict["title"] = self.titles[pcmh]
                    pcmh_dict["elements"] = {}
                    pcmh_dict["booleans"] = []
                    self.all_questions.append(pcmh_dict)

                element_dict = {element: Storage(description=description, label=label, element=element, func=func, done=False,
                                              url=URL('2014', func_name, vars=request.get_vars))}
                pcmh_dict["booleans"].append(is_complete)
                pcmh_dict["elements"].update(element_dict)


def _get_emr_image_rel_url(file_name):
    """
    :param file_name: A string like '<image>.png'
    :return url_path: A string to be used in web2py URL

    Checks to see if pcmh image exists for EMR, if not it returns generic version in root pcmh image folder.
    """
    static_real_path = os.path.join(os.getcwd(), request.folder, os.path.normpath("static/pcmh"))
    rel_path = os.path.join(APP.emr_std(), file_name)
    if os.path.exists(os.path.join(static_real_path, rel_path)):
        return "pcmh/%s/%s" % (APP.emr_std(), file_name)
    return "pcmh/%s" % file_name


# (0)###################################################


def pcmh_0_emr():
    """Electronic Medical Record Info"""
    #
    # if APP.emr in CLOUD_EMRS:
    #     FAKE_DB['emr_credentials'].website.requires = IS_URL()

    account_created = MultiQNA(
        1,1,
        True,
        'account_created',
        "Insight Management requires access to <b>%s</b> via a login that has provider or admin level access. "
        "Do you have this login information ready?" % APP.emr if APP.emr_std != "other" else "the EMR"
    )

    account_created.set_template(
        "{please_choose}")

    account_created.add_warning(getattr(account_created.row, "please_choose", None) in NOT_YES,
                                XML(T(
                                    "Please create provide an account that has provider or admin level access.")))

    emr_credentials = CryptQNA(
        1, float("inf"),  # change the 3 to the number of days the practice is open from the info
        getattr(account_created.row, "please_choose", None) == "Yes",
        'emr_credentials',
        "Please provide the username and password to the {emr} account that was created for "
        "Insight Management.".format(emr=APP.emr),
    )

    emr_credentials.set_template(
        "{gpg_encrypted}")

    # emr_login = MultiQNA(
    #     1, float("inf"),  # change the 3 to the number of days the practice is open from the info
    #     getattr(account_created.row, "please_choose", None) == "Yes",
    #     'emr_login',
    #     "Please provide the username and password to the {emr} account that was created for "
    #     "Insight Management.".format(emr=APP.emr),
    # )
    #
    # emr_login.set_template("Site: {website} <br>User: {username}<br>Password: {password}")
    #
    return dict(documents=[])


def pcmh_0_payment():
    """Credit Card"""

    payment_type = MultiQNA(
        1, 1,
        True,
        'payment_type',
        "A credit card or check is required to purchase the application tool(s) ($80/ea) and survey tool ($440). What "
        "form of payment will you use?"
    )

    payment_type.set_template("{please_choose}")

    credit_card = CryptQNA(
        1, float("inf"),  # change the 3 to the number of days the practice is open from the info
        getattr(payment_type.row, "please_choose", None) == "Credit Card", 'credit_card',
        "Please enter credit card information now.",
    )

    credit_card.set_template(
        "{gpg_encrypted}")
    return dict(documents=[])


def pcmh_0_agreements():
    """agreements"""

    baa_url = URL('init', 'static', 'documents/insight_pcmh_baa.DOC')
    tpa_url = URL('init', 'static', 'documents/pcmh_transformation_process_practice_letter.pdf')

    baa = MultiQNA(
        1, float("inf"),
        True,
        'baa',
        "Please review and sign <a href='{baa}'>this BAA agreement</a>.".format(
            practice=APP.practice_name,
            baa=baa_url,
            tpa=tpa_url,
        ),
    )

    baa.set_template("{choose_file}")

    tpa = MultiQNA(
        1, float("inf"),
        True,
        'tpa',
        "Please review and sign this <a href='{tpa}'>transformation process agreement</a>.".format(
            practice=APP.practice_name,
            baa=baa_url,
            tpa=tpa_url,
        ),
    )

    tpa.set_template("{choose_file}")

    return dict(documents=[
        dict(
            description="insight_pcmh_baa.doc",
            url=baa_url,
            permissions=["IS_TEAM"]
        ),
        dict(
            description="pcmh_transformation_process_practice_letter.pdf",
            url=tpa_url,
            permissions=["IS_TEAM"]
        ),
    ])


# def pcmh_0_ncqa():     """NCQA logins"""
#     application = CryptQNA(
#         1, 1,
#         True,
#         'ncqa_app',
#         "Enter the login information for the application tool."
#     )
#     application.set_template(
#         "{gpg_encrypted}")
#
#     iss = CryptQNA(
#         1, 1,
#         True,
#         'ncqa_iss',
#         "Enter the login information for the ISS survey tool."
#     )
#     iss.set_template(
#         "{gpg_encrypted}")
#
#     return dict(documents=[])


# (1a)###################################################

def pcmh_1_1a__1():
    """Scheduling"""

    office_hours = MultiQNA(
        3, float("inf"),
        True,
        'office_hours',
        "What are {practice}'s business hours? Note, these must be days <b>when patients are seen</b>.".format(
            practice=APP.practice_name),
        validator=_validate_start_end_time,
    )

    office_hours.set_template("{day_of_the_week} {start_time:%I}:{start_time:%M} "
                              "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}")

    office_hour_rows = db(db.office_hours.application == APP_ID).select()

    block_days = map(lambda e: e[0],
                     sorted(
                         set(
                             map(lambda e: (e.day_of_the_week,
                                            DAYS_OF_THE_WEEK.index(e.day_of_the_week)),
                                 office_hour_rows)
                         ), key=lambda e: e[1])
                     )  # can have multiple Thurs, make unique

    db.same_day_block.day_of_the_week.requires = \
        IS_IN_SET(block_days, zero=None)

    same_day_appointments = MultiQNA(
        1, 1,
        len(office_hour_rows) >= 3,
        'same_day_appointments',
        "Does the practice visibly block time on the scheduler <span class='dotted-underline'>every day</span> "
        "for same-day appointments?"
    )

    same_day_appointments.set_template("{please_choose}")

    same_day_appointments.add_warning(
        getattr(same_day_appointments.row, "please_choose", None) in NOT_YES,
        "{practice} <b>must</b> reserve time every business day (when patients are seen) for same-day appointments. "
        "There is <b>no</b> exception to this rule, even for practices that are primarily walk-in clinics. "
        "We recommend one or two 15-minute slots reserved visibly in your schedule. The practice cannot pre-schedule "
        "appointments over a same-day block, except on the very same day of the block. If the block is never used, "
        "then practice may replace it with a walk-in patient.{carousel}".format(
            practice=APP.practice_name,
            carousel=CAROUSEL("same_day_appointments", [
                ("1. Set the block", "Double-click an open slot on your scheduler and block some time for same-day "
                                     "appointments.",
                 URL('static', _get_emr_image_rel_url('same_day_appointment_setting.png'))),
                ("2. Repeat", "Repeat this for every day your practice is open. "
                              "You need at least one 15-minute block per day.",
                 URL('static', _get_emr_image_rel_url('same_day_appointment_set.png')))
            ])
        )
    )

    same_day_blocks = MultiQNA(
        len(block_days), float("inf"),  # change the 3 to the number of days the practice is open from the info
        getattr(same_day_appointments.row, "please_choose", None) == "Yes",
        'same_day_block',
        "Enter your same-day appointment blocks. Remember, there should be at least one same-day appointment block "
        "for <b>each day of the week when patients are seen.</b>",
        validator=_validate_start_end_time,
    )

    same_day_blocks.set_template("{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                 "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}")

    same_day_block_rows = db(db.same_day_block.application == APP_ID).select()

    if len(same_day_block_rows) >= len(block_days):
        diff = set(map(lambda e: e.day_of_the_week, same_day_block_rows)).symmetric_difference(block_days)
        same_day_blocks.add_warning(diff, "You are missing same-day block(s) for %s." % ", ".join(sorted(diff)))

    return dict(documents=[
        # ("PCMH_1A_4.doc", URL("init", "policy", "PCMH_1A_4.doc"))
    ])


def pcmh_1_1a__2():
    """After hours"""

    extra = " For example, in an office with typical business hours from 9AM - 5PM, " \
            "the following examples are considered extended business hours for seeing patients:<small>" \
            "<ul><li>Monday - Thursday 9AM - 5PM, Friday 10AM - 6PM (shift in hours for one day of the week)</li>" \
            "<li>Monday - Thursday 9AM - 5PM, Friday 9AM - 6PM (extra hours for one day of the week)</li>" \
            "<li>Monday - Friday 9AM - 5PM, Saturday 9AM - 3PM (extra day during a weekend)</li></ul></small>"

    after_hours = MultiQNA(
        1, 1, True,
        'after_hours',
        "Does the practice see patients outside regular business hours?"
    )

    after_hours.set_template("{please_choose}")

    after_hours.add_warning(
        getattr(after_hours.row, "please_choose", None) in NOT_YES,
        "The practice is recommended to see patients during extended business hours at least "
        "once a week. Please note, that this does not include the provider \"staying late\" on some days; this must be "
        "implemented as a policy of the practice." + extra
    )

    after_hour_blocks = MultiQNA(
        1, float("inf"),
        getattr(after_hours.row, "please_choose", None) == "Yes",
        'after_hour_block',
        "Please enter your extended business hours here.",
        validator=_validate_start_end_time,
    )

    after_hour_blocks.set_template("{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                   "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}")

    documents = []

    if len(db(db.office_hours.application == APP_ID).select()) >= 3 and after_hour_blocks.rows:
        documents.append(dict(
            description="policy_1a2_after_hours.doc",
            url=URL('init', 'word', 'policy_1a2_after_hours.doc',
                        vars=dict(**request.get_vars), hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"]),
            permissions=["IS_TEAM"]
        ))

    return dict(documents=documents)


def pcmh_1_1a__4():
    """Availability of appointments"""

    availability_of_appointments = MultiQNA(
        1, 1, True,
        'availability_of_appointments',
        "What is {practice}'s next available appointment for the "
        "following visit types?".format(practice=APP.practice_name)
    )

    availability_of_appointments.set_template("<ul>"
                                              "<li>New Patient: {new_patient} day(s)</li>"
                                              "<li>Urgent: {urgent} day(s)</li>"
                                              "<li>Consult: {consult}  day(s)</li>"
                                              "<li>Walk-in: {walk_in} days(s)</li>"
                                              "<li>Same-day: {same_day} day(s)</li>"
                                              "</ul>")

    return dict(documents=[])


def pcmh_1_1a__5():
    """Monitoring no-shows"""

    no_show_name = '"no-show" (or a similar field in the EMR)'
    if APP.emr == "practice_fusion":
        no_show_name = '"no show"'

    no_show_emr = MultiQNA(
        1, 1,
        True,
        'no_show_emr',
        'For at least the last 30 days, did the practice regularly mark appointments as {no_show_name} '
        'when patients did not show up for their scheduled appointments?'.format(no_show_name=no_show_name)
    )

    no_show_emr.set_template("{please_choose}")

    no_show_emr.add_warning(
        getattr(no_show_emr.row, "please_choose", None) in NOT_YES,
        'The practice must mark appointments as {no_show_name} <b>every time</b> a patient does not '
        'show up to his/her scheduled appointment. This is required to properly run no-show reports. It is recommended '
        'that the practice retrospectively changes all appointment statuses to the proper field for the last 30 days, '
        'so that a no-show report can be obtained as soon as possible.  Please change your answer to "Yes" when '
        'you have over 30 days of properly set appointment statuses.{carousel}'.format(
            no_show_name=no_show_name,
            carousel=
            CAROUSEL(
                "no_show_emr",
                [("Flag no-shows",
                  "If a patient does not show up to his/her scheduled appointment, DO NOT leave it as \"Pending "
                  "Arrival\"", URL('static', _get_emr_image_rel_url('mark_as_no_show.png')))]
            ),
        )
    )

    # no_show_report_date_range = MultiQNA(
    #     1, 1,
    #     True,
    #     'no_show_report_date_range',
    #     "Please choose a date range where we will be able to run a no-show report with properly set appointment "
    #     "statuses (i.e. seen, no-show)"
    # )

    return dict(documents=[
        dict(
            description="policy_1a5_no_show.doc",
            url=URL('init', 'word', 'policy_1a5_no_show.doc',
                    vars=dict(**request.get_vars), hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"]),
            permissions=["IS_MANAGER"]
        ),
    ])


# (1b)###################################################\
def pcmh_1_1b__1_2_3_4():
    """Clinical advice (telephone encounters)"""

    telephone_encounter_table_url = URL('init', 'word', 'telephone_log.doc',
                                        vars=dict(type="meeting", **request.get_vars),
                                        hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"])

    telephone_encounter_log_usage = MultiQNA(
        1, 1,
        True,
        'telephone_encounter_log_usage',
        "Does {practice} use <a href='{url}'>this telephone encounter log</a> (or an equivalent system) to track "
        "<b>telephone encounters</b>?"
        .format(practice=APP.practice_name, url=telephone_encounter_table_url)
    )

    telephone_encounter_log_usage.set_template("{please_choose}")

    telephone_encounter_log_usage.add_warning(
        getattr(telephone_encounter_log_usage.row, "please_choose", None) in NOT_YES,
        "{practice} must keep a log of all telephone encounters and document advice given to patents into the patient "
        "record (refill requests alone do not satisfy the PCMH standard).{carousel}".format(
            practice=APP.practice_name,
            carousel=
            CAROUSEL(
                "telephone_encounter_log",
                [("Document time and date information",
                  "Immediately after a telephone call, record the date and approximate time of when the call was "
                  "received and when the call was addressed. If there are no telephone encounters for a given day, "
                  "write <i>No Clinical Advice</i>. We recommend using this <a href='{url}'>this telephone encounter "
                  "log</a> (or an equivalent system) to track telephone encounters.".format(
                      url=telephone_encounter_table_url),
                  URL('static', _get_emr_image_rel_url('telephone_encounter_log.png')))]
            )
        )
    )

    telephone_encounter_in_record = MultiQNA(
        1, 1,
        True,
        'telephone_encounter_in_record',
        "Does {practice} document telephone advice given to patients into the patient record?"
        .format(practice=APP.practice_name, url=telephone_encounter_table_url)
    )

    telephone_encounter_in_record.add_warning(
        getattr(telephone_encounter_in_record.row, "please_choose", None) in NOT_YES,
        "{practice} must document <b>advice</b> given to patents into the patient "
        "record (refill requests alone do not satisfy the PCMH standard).{carousel}".format(
            practice=APP.practice_name,
            carousel=
            CAROUSEL(
                "telephone_encounter",
                [("1. Create Encounter",
                  "In the patient's chart, create a new encounter.",
                  URL('static', _get_emr_image_rel_url('telephone_encounter_create2.png'))),
                 ("2. Describe Encounter",
                  "Describe when the call was received, when the call was ended/addressed, and a summary of the call. "
                  "Note if patient expresses understanding of the advice given.",
                  URL('static', _get_emr_image_rel_url('telephone_encounter_ex.png')))]
            )
        )
    )

    telephone_encounter_in_record.set_template("{please_choose}")

    telephone_encounter_log = MultiQNA(
        1, float("inf"),
        getattr(telephone_encounter_log_usage.row, "please_choose", None) == "Yes",
        'telephone_encounter_log',
        "Please upload logs consisting of at least 7 consecutive "
        "business days' worth of telephone encounters. Only include incoming encounters seeking advice (refill "
        "requests do not meet the standard). Be sure to document the advice and time/date information into the "
        "corresponding patient record."
    )

    telephone_encounter_log.set_template("{choose_file}")

    # telephone encounter examples
    # completed_log_file_description = getattr(telephone_encounter_log.row, "file_description", "")
    completed_log_file_name = getattr(telephone_encounter_log.rows.last(), "choose_file", "")
    completed_log_url = URL("init", request.controller, "download", args=[completed_log_file_name],
                            vars=dict(**request.get_vars))

    temp = "Please provide <b>%s</b> patient%s <a href='{url}'>from your telephone encounter log</a> where the " \
           "advice was documented into the patient record <b>%s business hours</b>".format(url=completed_log_url)

    telephone_encounter_during_hours_example = MultiQNA(
        2, 2, telephone_encounter_log.rows,
        'telephone_encounter_during_hours_example',
        temp % (2, "s", "during")
    )

    telephone_encounter_during_hours_example\
        .set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

    telephone_encounter_after_hours_example = MultiQNA(
        1, 1, telephone_encounter_log.rows,
        'telephone_encounter_after_hours_example',
        temp % (1, "", "after")
    )

    telephone_encounter_after_hours_example \
        .set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

    return dict(documents=[
        dict(
            description="Telephone Encounter Log",
            url=telephone_encounter_table_url,
            permissions=["IS_TEAM"]
        ),
    ])

# def pcmh_1_1c__1_2_3_4_5_6():
#     """Meaningful use"""
#     meaningful_use = MultiQNA(
#         1, float("inf"),
#         True,
#         'meaningful_use',
#         "Please upload your most recent meaningful use report."
#     )
#
#     meaningful_use.set_template("{choose_file}")
#
#     return dict(documents=[])


# (2)###################################################
def pcmh_2_2d__1_2():
    """Team Structure"""

    providers = MultiQNA(
        1, float("inf"),
        True,
        'provider',
        "Please enter your staff who <b>are</b> providers.",
    )

    providers.set_template(
        "<b class='text-success'>{first_name} {last_name}, {role}</b>"
        "<br>&emsp;Usually in office on: {days_of_the_week}"
        "<br>&emsp;DEA: {dea}"
        "<br>&emsp;NPI: {npi}"
        "<br>&emsp;License: {license}"
        "<br>&emsp;Bills Under: {bills_under}"
    )

    other_staff = MultiQNA(
        1, 1,
        True,
        'other_staff',
        "Do you have any staff who <b>are not</b> providers? (i.e. MAs, front desk, office manager, etc.)?"
    )

    other_staff.set_template(
        "{please_choose}")

    staff = MultiQNA(
        1, float("inf"),  # change the 3 to the number of days the practice is open from the info
        getattr(other_staff.row, "please_choose", None) == "Yes",
        'staff',
        "Please enter your staff who <b>are not</b> providers.",
    )

    staff.set_template(
        "{quantity}x {role}")

    return dict(documents=[])


def pcmh_2_2d__3_5_6_7_8():
    """Huddles, Meetings & Trainings"""

    huddle_sheet_url = URL('init', 'word', 'huddle_sheet.doc', vars=dict(**request.get_vars), hmac_key=MY_KEY,
                           salt=session.MY_SALT, hash_vars=["app_id"])

    # referral tracking chart
    huddle_sheet = MultiQNA(
        5, float('inf'), True,
        'huddle_sheet',
        "Please upload a minimum of 5 days' worth of <a href='{url}'>daily huddle sheets</a>. The huddles must filled "
        "out every morning discussing tasks / reminders regarding a particular patient or a population of "
        "patients.".format(url=huddle_sheet_url)
    )

    huddle_sheet.set_template("{choose_file}")

    temp = "Please have all staff sign <a href='{url}'>this %s sign-in sheet</a> the next time " + \
           "{practice} conducts a %s.".format(practice=APP.practice_name)

    # meeting_sheet
    meeting_sheet_url = URL('init', 'word', 'signin_sheet.doc', args=["meeting_signin_sheet"],
                            vars=dict(type="meeting", **request.get_vars),
                            hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"])

    meeting_sheet = MultiQNA(
        1, 1, True,
        'meeting_sheet',
        (temp % ("meeting", "meeting to discuss practice functioning")).format(
            url=meeting_sheet_url)
    )

    meeting_sheet.set_template("{choose_file}")

    # meeting_sheet
    training_sheet_url = URL('init', 'word', 'signin_sheet.doc', args=["training_signin_sheet"],
                             vars=dict(type="training", **request.get_vars),
                             hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"])

    training_sheet = MultiQNA(
        1, float('inf'), True,
        'training_sheet',
        (temp % ("training", "training / re-training regarding patient and population management")).format(
            url=training_sheet_url)
    )

    training_sheet.set_template("{choose_file}")

    return dict(documents=[
        dict(
            description="Daily Huddle Sheet",
            url=huddle_sheet_url,
            permissions=["IS_TEAM"]
        ),
                dict(
            description="Training Sign-in Sheet",
            url=training_sheet_url,
            permissions=["IS_TEAM"]
        ),
                dict(
            description="Meeting Sign-in Sheet",
            url=meeting_sheet_url,
            permissions=["IS_TEAM"]
        ),

    ])


def pcmh_2_2c__1___4a__6():
    """Patient Population"""
    patient_population = MultiQNA(
        1, 1, True, "patient_population",
        "What is the estimated total number of active patients in {practice}?".format(practice=APP.practice_name)
    )

    patient_population.set_template("{patients}")

    race = MultiQNA(
        1, 1, True, "race",
        "Out of <b>100 patients</b>, what is the estimated number of patients in {practice} "
        "who represent each of the following races? The total of these numbers must add up to 100."
        .format(practice=APP.practice_name),
        validator=lambda form:
        _on_validation_100(form, fields=["native_american", "pacific_islander", "black", "white", "east_asian",
                                         "south_asian"]),
    )

    race.set_template("<ul>"
                      "<li>Native American {native_american}</li>"
                      "<li>Pacific Islander {pacific_islander}</li>"
                      "<li>Black {black}</li>"
                      "<li>White {white}</li>"
                      "<li>East Asian {east_asian}</li>"
                      "<li>South Asian {south_asian}</li>"
                      "</ul>")

    ethnicity = MultiQNA(
        1, 1, True, "ethnicity",
        "Out of <b>100 patients</b>, what is the estimated number of patients in {practice} "
        "who represent each of the following ethnicities? The total of these numbers must add up to 100."
        .format(practice=APP.practice_name),
        validator=lambda form:
        _on_validation_100(form, fields=["non_hispanic", "hispanic"]),
    )

    ethnicity.set_template("<ul>"
                           "<li>Non-Hisanic {non_hispanic}</li>"
                           "<li>Hispanic {hispanic}</li>"
                           "</ul>")

    gender = MultiQNA(
        1, 1, True, "gender",
        "Out of <b>100 patients</b>, what is the estimated number of patients in {practice} "
        "who represent each of the following genders? The total of these numbers must add up to 100."
        .format(practice=APP.practice_name)
    )

    gender.set_template("<ul>"
                           "<li>Male {male}</li>"
                           "<li>Female {female}</li>"
                           "<li>Other {other}</li>"
                           "</ul>")

    language = MultiQNA(
        1, 1, True, "languages",
        "Out of <b>100 patients</b>, what is the estimated number of patients in {practice} "
        "who represent each of the following languages? The total of these numbers must add up to 100."
        .format(practice=APP.practice_name),
        validator=lambda form:
        _on_validation_100(form, fields=["english", "spanish", "chinese", "hindi", "bengali", "arabic", "african"]),
    )

    language.set_template("<ul>"
                          "<li>English {english}</li>"
                          "<li>Spanish {spanish}</li>"
                          "<li>Chinese {chinese}</li>"
                          "<li>Hindi {hindi}</li>"
                          "<li>Bengali {bengali}</li>"
                          "<li>Arabic {arabic}</li>"
                          "<li>African {african}</li>"
                          "</ul>"
                          )
    documents = []

    if patient_population.row and ethnicity.row and race.row and language.row:
        demographic_report_url = \
            URL('init', 'word', 'report_2c_factor_1_2_demographics.doc',
                vars=dict(denominator=patient_population.row["patients"],
                          hispanic=ethnicity.row["hispanic"],
                          non_hispanic=ethnicity.row["non_hispanic"],
                          black=race.row["black"],
                          white=race.row["white"],
                          native_american=race.row["native_american"],
                          pacific_islander=race.row["pacific_islander"],
                          south_asian=race.row["south_asian"],
                          east_asian=race.row["east_asian"],
                          male=gender.row["male"],
                          female=gender.row["female"],
                          other=gender.row["other"],
                          english=language.row["english"], 
                          spanish=language.row["spanish"],
                          chinese=language.row["chinese"],
                          hindi=language.row["hindi"],
                          bengali=language.row["bengali"],
                          arabic=language.row["arabic"],
                          african=language.row["african"],
                          south_central_american=race.row["south_central_american"],
                          **request.get_vars),
                hmac_key=MY_KEY, salt=session.MY_SALT,
                hash_vars=["app_id",
                           "denominator", "hispanic", "non_hispanic", "black", "white", "native_american",
                           "pacific_islander", "south_asian", "east_asian", "male", "female", "other",
                           "english", "spanish", "chinese", "hindi", "bengali", "arabic", "african",
                           "south_central_american"])
        documents.append(dict(
            description="report_2c_factor_1_2_demographics.doc",
            url=demographic_report_url,
            permissions=["IS_TEAM"]
        ))

    return dict(documents=documents)

# (3)###################################################


def pcmh_3_3a__1_2_3_4_5_6_7_9_10_11_12_13_14():
    """Patient Demographics"""

    patient_demographics_choices = ['Date of birth', 'Sex', 'Race', 'Ethnicity', 'Preferred language',
                                    'Telephone numbers', 'E-mail address', 'Occupation',
                                    'Dates of previous clinical visits', 'Legal guardian/health care proxy',
                                    'Primary caregiver', 'Presence of advance directives (pediatrics only)',
                                    'Health insurance information', 'Name and contact information of other health care '
                                                                    'professionals involved in patient\'s care.']
    minimum = 10

    if APP.practice_specialty == "Pediatrics":
        patient_demographics_choices = filter(lambda t: t[0] not in [7, 9], patient_demographics_choices)
        minimum = 8

    db.patient_demographics.please_choose.requires = IS_IN_SET(patient_demographics_choices, multiple=True)

    patient_demographics = MultiQNA(
        1, 1, True,
        'patient_demographics',
        "For each patient, which of the following demographic fields does %s record either in the patient's care notes "
        "or in structured fields?" % APP.practice_name
    )

    choices = getattr(patient_demographics.row, "please_choose", None)

    if choices:
        patient_demographics.add_warning(
            len(choices) < minimum,
            "{pc} <b>must record at least {min}</b> of these choices either in the care notes or in structured fields "
            "(only {max}/{min} picked): {li} Please fill out more of these fields for your new and recent patients. "
            "Then come back and change your answer.".format(pc=APP.practice_name, min=minimum, max=len(choices),
                                                       li=OL(*map(lambda e: LI(e), patient_demographics_choices)))
        )

    patient_demographics.set_template("{please_choose}")
    return dict(documents=[])


def pcmh_3_3c__1_2_3_4_5_6_7_9_10():
    """Comprehensive Health Assessment"""
    medical_history = MultiQNA(
        1, float("inf"), True,
        "medical_history",
        "Please provide patient(s) with detailed <b>cultural, social, medical and mental health history</b>."
        .format(measure_description=_each[1])
    )

    medical_history.set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

    family_history = MultiQNA(
        1, float("inf"), True,
        "family_history",
        "Please provide patient(s) with a detailed cultural, social, medical and mental health history of the <b>"
        "family member(s)</b>."
        .format(measure_description=_each[1])
    )

    family_history.set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")


    return dict(documents=[])


def pcmh_3_3d__1_2_3_4_5():
    """Patient callback"""

    services = [("immunization", "vaccinations/immunizations"),
                ("preventative", "preventative"),
                ("chronic", "chronic/acute")]

    temp = "Please upload callback / missing service lists for <b>2 {svc}</b> measures. Documents can be sourced " \
        "from {emr}, QARR/HEDIS (from 3 or more health plans), and/or CIR recall lists. Documents must be dated " \
        "within the last 10 months."

    for svc in services:
        qna = MultiQNA(
            1, float("inf"), True,
            'callback_list_%s' % svc[0],
            temp.format(emr=APP.emr, svc=svc[1])
        )

        qna.set_template("{choose_file}")

    return dict(documents=[])

# (4)###################################################


def pcmh_4_4a__1_2_3():
    """Care Management"""
    icd_behavioral = MultiQNA(
        1, 1, True, "icd_behavioral",
        "Please enter some ICD 10 codes that {practice} uses for <b>behavioral health</b> (i.e. depression, anxiety, "
        "etc).".format(practice=APP.practice_name)
    )

    icd_behavioral.set_template("{icd}")

    icd_acute = MultiQNA(
        1, 1, True, "icd_acute",
        "Please enter some ICD 10 codes that {practice} uses for <b>acute conditions</b> (i.e. pneumonia, cervicalgia, "
        "etc).".format(practice=APP.practice_name)
    )

    icd_acute.set_template("{icd}")

    icd_chronic = MultiQNA(
        1, 1, True, "icd_chronic",
        "Please enter some ICD 10 codes that {practice} uses for <b>chronic conditions</b> (i.e. hypertension, asthma, "
        "etc).".format(practice=APP.practice_name)
    )

    icd_chronic.set_template("{icd}")

    icd_well = MultiQNA(
        1, 1, True, "icd_well",
        "Please enter some ICD 10 codes that {practice} uses for <b>well or annual visits</b>."
        .format(practice=APP.practice_name)
    )

    icd_well.set_template("{icd}")

    return dict(documents=[])


def pcmh_4_4b__1_2_3_4_5___3e__1_2_3_4_5():
    """Care plans"""

    is_pediatrics = APP.practice_specialty == "Pediatrics"

    care_plan = MultiQNA(
        1, 1, True, "care_plan",
        ("For <b>every care plan</b>, does {practice} thoroughly discuss or assess <b>all</b> of the following? "
         "(Choose \"No\" to see an example)"
         "<small><ul><li>Prescription and OTC risk / reward / usage / understanding</li>"
         "<li>Patient goals / preferences / life-style</li>"
         "<li>Patient barriers to maintaining treatment plan or medications</li>"
         "<li>labs / screenings / referrals ordered</li>"
         "<li>Resources or materials given to patient or family</li>"
         "<li>Recent hospitalizations or self-referrals</li>%s</small>" %
         (" " if is_pediatrics else "<li>Advanced directives</li>")
         ).format(practice=APP.practice_name)
    )

    care_plan.set_template("{please_choose}")

    care_plan.add_warning(
        getattr(care_plan.row, "please_choose", None) in NOT_YES,
        "The following should be templated into <b>every care plan</b> and thoroughly answered when applicable:<ol>"
        "<li>Has the patient been recently hospitalized or self-referred?</li>"
        "<li>Describe the patient's goals, preferences and any life-style changes discussed:</li>"
        "<li>Describe patient's barriers to treatment plan or medications and any solutions discussed:</i>"
        "<li>Describe the discussion of risk / reward / proper usage of medications / OTCs / Herbals with patient:</li>"
        "<li>Describe materials / resources given to patient or family:</li>"
        "%s</ol>"
        "The following should be templated to the <b>end of every care plan</b>: <ul><li>Reviewed Treatment Care Plan "
        "and Treatment Goals. Assessed and addressed potential barriers to meeting treatment goals and medication "
        "adherence. Printout of Care plan, information about new prescriptions, and progress note was given to "
        "patient. Patient acknowledged understanding of prescribed medications and treatment care plan.</li></ul>%s"
        % ("" if is_pediatrics else "<li>Describe the discussion of advanced care planning with the patient:</li>",
           CAROUSEL(
               "care_plan_example",
               [(
                   "Care Plan Example",
                   "This is an example of an assessment care plan that contains the questions and text above.",
                   URL('static', _get_emr_image_rel_url('care_plan_example_1.png')))])))

    for _each in MEASURES_3E:
        measure = MultiQNA(
            1, float("inf"), care_plan.row,
            _each[0],
            "Please provide a patient with a detailed evidence-based care plan for <b>{measure_description}</b>. "
            .format(measure_description=_each[1])
        )

        measure.set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

    return dict(documents=[])

# (5)###################################################


def pcmh_5_5a__1_2_3_4_5_6___5b__5_6_8():
    """Lab, Image, Referral Tracking & Follow-Up"""

    documents = [
    ]

    if APP.practice_specialty == "Pediatrics":
        developmental_screening = MultiQNA(
            1, 1, True,
            'developmental_screening',
            "Please enter an infant patient where a completed developmental screening tool can be found in the "
            "patient's portal. <b>Alternatively</b>, enter an infant patient where sequential and thorough care notes "
            "tracking the development of the infant can be found in the patient's portal."
        )
        developmental_screening.set_template("{please_choose}")

    temp = "Does {practice} use <a href='{table_url}'>this {order_type} tracking table</a> (or an equivalent system) " \
           "to track <b>{order_type} orders</b>?"
    _imaging = "imaging (X-Ray, MRI, Sonogram, EKG etc.)"

    if not APP.emr_std() in ["mdland_iclinic"]:
        # image tracking
        image_table_url = URL('init', 'word', 'tracking_chart.doc', args=["image_order_tracking_chart"],
                              vars=dict(type="image", **request.get_vars),
                              hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"])

        documents.append(
            dict(
                description="Image Order Tracking Log",
                url=image_table_url,
                permissions=["IS_TEAM"]
            )
        )

        image_tracking = MultiQNA(
            1, 1, True,
            'image_tracking', temp.format(
                practice=APP.practice_name, order_type=_imaging, table_url=image_table_url)
        )
        image_tracking.set_template("{please_choose}")

    if not APP.emr_std() in ["mdland_iclinic"]:
        # lab tracking
        lab_table_url = URL('init', 'word', 'tracking_chart.doc', args=["lab_order_tracking_chart"],
                            vars=dict(type="lab", **request.get_vars),
                            hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"])

        documents.append(
            dict(
                description="Lab Order Tracking Log",
                url=lab_table_url,
                permissions=["IS_TEAM"]
            )
        )

        lab_tracking = MultiQNA(
            1, 1, True,
            'lab_tracking', temp.format(
                practice=APP.practice_name, order_type="lab", table_url=lab_table_url)
        )
        lab_tracking.set_template("{please_choose}")
    
    # referral tracking
    referral_table_url = URL('init', 'word', 'tracking_chart.doc', args=["referral_order_tracking_chart"],
                             vars=dict(type="referral", **request.get_vars),
                             hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"])

    documents.append(
        dict(
            description="Referral Order Tracking Log",
            url=referral_table_url,
            permissions=["IS_TEAM"]
        ))

    referral_tracking = MultiQNA(
        1, 1, True,
        'referral_tracking', temp.format(
            practice=APP.practice_name, order_type="referral", table_url=referral_table_url)
    )
    referral_tracking.set_template("{please_choose}")

    temp = "{practice} should use <a href='{chart_url}'>this table</a> (or an equivalent tracking system) to track " \
           "{order_type} orders to best meet PCMH requirements"

    if not APP.emr_std() in ["mdland_iclinic"]:
        image_tracking.add_warning(
            getattr(image_tracking.row, "please_choose", None) in NOT_YES,
            temp.format(practice=APP.practice_name, chart_url=image_table_url, order_type=_imaging)
        )

    if not APP.emr_std() in ["mdland_iclinic"]:

        lab_tracking.add_warning(
            getattr(lab_tracking.row, "please_choose", None) in NOT_YES,
            temp.format(practice=APP.practice_name, chart_url=lab_table_url, order_type="lab")
        )

    referral_tracking.add_warning(
        getattr(referral_tracking.row, "please_choose", None) in NOT_YES,
        temp.format(practice=APP.practice_name, chart_url=referral_table_url, order_type="referral")
    )

    temp = "Please upload <b>{order_type} tables</b> that has at least 5 days' worth of orders that was tracked from " \
           "start (order sent) to finish (results received). At least one row in the tables should depict an overdue " \
           "order and corresponding follow-up action."

    if not APP.emr_std() in ["mdland_iclinic"]:
        # image tracking chart
        image_tracking_chart = MultiQNA(
            1, float('inf'), image_tracking.row,
            'image_tracking_chart',
            temp.format(order_type=_imaging)
        )

        image_tracking_chart.set_template("{choose_file}")

    if not APP.emr_std() in ["mdland_iclinic"]:
        # lab tracking chart
        lab_tracking_chart = MultiQNA(
            1, float('inf'), lab_tracking.row,
            'lab_tracking_chart',
            temp.format(order_type="lab")
        )

        lab_tracking_chart.set_template("{choose_file}")

    # referral tracking chart
    referral_tracking_chart = MultiQNA(
        1, float('inf'), referral_tracking.row,
        'referral_tracking_chart',
        temp.format(order_type="referral")
    )

    referral_tracking_chart.set_template("{choose_file}")

    temp = "Does {practice} contact patients every time when <b>%s results </b> arrive regardless if it's normal or " \
           "abnormal? ".format(practice=APP.practice_name)

    if not APP.emr_std() in ["mdland_iclinic"]:
        # lab follow up
        lab_follow_up = MultiQNA(
            1, 1, lab_tracking.row,
            'lab_follow_up', temp % "lab")

        lab_follow_up.set_template("{please_choose}")

    if not APP.emr_std() in ["mdland_iclinic"]:
        # image follow up
        image_follow_up = MultiQNA(
            1, 1, image_tracking.row,
            'image_follow_up', temp % _imaging)

        image_follow_up.set_template("{please_choose}")

    # referral follow up
    referral_follow_up = MultiQNA(
        1, 1, referral_tracking.row,
        'referral_follow_up', temp % "referral")

    referral_follow_up.set_template("{please_choose}")

    temp = "The practice must contact the patient regarding <b>%s results</b> for both <b>normal</b> and " \
           "<b>abnormal</b> results. This contact must be captured as a telephone encounter or a letter in the " \
           "patient record."

    if not APP.emr_std() in ["mdland_iclinic"]:
        lab_follow_up.add_warning(
            getattr(lab_follow_up.row, "please_choose", None) in NOT_YES,
            temp % "lab")

    if not APP.emr_std() in ["mdland_iclinic"]:
        image_follow_up.add_warning(
            getattr(image_follow_up.row, "please_choose", None) in NOT_YES,
            temp % _imaging)
    
    referral_follow_up.add_warning(
        getattr(referral_follow_up.row, "please_choose", None) in NOT_YES,
        temp % "referral")

    temp = "Please provide 3 patients where {practice} created a telephone encounter " \
           "or letter to the patient regarding <b>%s</b> in the patient's record.".format(practice=APP.practice_name)

    if not APP.emr_std() in ["mdland_iclinic"]:
        # lab follow up example normal
        lab_follow_up_normal_example = MultiQNA(
            3, float('inf'), getattr(lab_follow_up.row, "please_choose", None) == "Yes",
            'lab_follow_up_normal_example', temp % "normal lab results"
            )

        lab_follow_up_normal_example\
            .set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

        # lab follow up example abnormal
        lab_follow_up_abnormal_example = MultiQNA(
            3, float('inf'), getattr(lab_follow_up.row, "please_choose", None) == "Yes",
            'lab_follow_up_abnormal_example', temp % "abnormal lab results")

        lab_follow_up_abnormal_example.\
            set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

    if not APP.emr_std() in ["mdland_iclinic"]:

        # image follow up example normal
        image_follow_up_normal_example = MultiQNA(
            3, float('inf'), getattr(image_follow_up.row, "please_choose", None) == "Yes",
            'image_follow_up_normal_example', temp % "normal imaging results")

        image_follow_up_normal_example.\
            set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

        # image follow up example abnormal
        image_follow_up_abnormal_example = MultiQNA(
            3, float('inf'), getattr(image_follow_up.row, "please_choose", None) == "Yes",
            'image_follow_up_abnormal_example', temp % "abnormal imaging results")

        image_follow_up_abnormal_example.\
            set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

    # referral follow up example normal
    referral_follow_up_normal_example = MultiQNA(
        3, float('inf'), getattr(referral_follow_up.row, "please_choose", None) == "Yes",
        'referral_follow_up_normal_example', temp % "normal referral results"
        )

    referral_follow_up_normal_example.\
        set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

    # referral follow up example abnormal
    referral_follow_up_abnormal_example = MultiQNA(
        3, float('inf'), getattr(referral_follow_up.row, "please_choose", None) == "Yes",
        'referral_follow_up_abnormal_example', temp % "abnormal referral results")

    referral_follow_up_abnormal_example.\
        set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

    # todo - add new born screening for peds

    return dict(documents=documents)

def pcmh_5_5b__1_2_3_5_6_7_8_9_10():
    """Care Coordination"""

    referral_blurb = MultiQNA(
        1, 1, True,
        'referral_blurb',
        "When making a referral to a specialist's or psychiatrist's office, does {practice} include the patient's "
        "latest demographics (i.e. care plan, medications, etc.), the latest lab/screening/test results and the "
        "following <b>informal agreement?</b> <small><p><ul><li>In referring this patient to your care, our office "
        "expects in return a full report regarding our patient’s visit within 7 days of the appointment. Additionally, "
        "please send any documentation regarding your diagnosis and any treatment options considered. If you have any "
        "questions please contact our office.</small></li></ul>".format(practice=APP.practice_name)
    )

    referral_blurb.set_template("{please_choose}")

    referral_blurb.add_warning(getattr(referral_blurb.row, "please_choose", None) in NOT_YES,
                               "Adding informal agreement to referral orders is a requirement in PCMH."
                               )

    temp = "Please upload a copy of a referral order recently sent to a <b>%s</b>. Make sure it includes the patient " \
           "demographics, latest lab/screening/test results and the informal agreement."\
           .format(practice=APP.practice_name)

    psych_order_example = MultiQNA(
        1, 1, referral_blurb.row,
        'psych_order_example', temp % "psychiatrist"
    )

    psych_order_example.set_template("{choose_file}")

    specialist_order_example = MultiQNA(
        1, 1, referral_blurb.row,
        'specialist_order_example', temp % "specialist"
    )

    specialist_order_example.set_template("{choose_file}")

    return dict(documents=[])


def pcmh_5_5c__3():
    """ER/IP discharge log"""
    er_ip_log_url = URL('init', 'word', 'er_ip_log.doc',
                        vars=dict(**request.get_vars),
                        hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"])
    # er_ip_log tracking chart
    er_ip_log = MultiQNA(
        1, float('inf'), True,
        'er_ip_log',
        "Please fill out <a href='{url}'>this ER/IP log</a> with at least 4 months of past data. Continue to maintain "
        "this log permanently as part of your PCMH transformation. <b>Please make sure all the patients in this log "
        "have their discharge summary in their patient record!</b>"
        .format(url=er_ip_log_url)
    )

    er_ip_log.set_template("{choose_file}")

    return dict(documents=[
        dict(
            description="Emergency Room / Inpatient Tracking Log",
            url=er_ip_log_url,
            permissions=["IS_TEAM"]
        ),
    ])

# (6)###################################################
def pcmh_6_6a__1_2_3_4():
    """Performance reports"""

    temp = "Please upload performance reports for <b>2 {svc}</b> measures. Documents can be sourced " \
        "from {emr}, QARR/HEDIS (from 3 or more health plans), and/or CIR. Documents must be dated " \
        "within the last 10 months."

    for svc in SERVICES:
        report_cards = MultiQNA(
            1, float("inf"), True,
            'report_card_%s' % svc[0],
            temp.format(emr=APP.emr, svc=svc[1])
        )

        report_cards.set_template("{choose_file}")

    award = MultiQNA(
        1, 1, True,
        'award',
        "Did {practice} ever receive any kind of award or letter of recognition from an external entity "
        "(i.e. MetroPlus QARR/HEDIS award in Chalymdia Screening) within the last 10 months?"
        .format(practice=APP.practice_name)
    )

    award.set_template("{please_choose}")

    award_document = MultiQNA(
        1, float("inf"), award.row,
        'award_document',
        "Please upload document containing an award or letter of recognition from an external entity regarding "
        "practice or Quality Measure performance".format()
    )

    award_document.set_template("{choose_file}")

    return dict(documents=[])

# (end)###################################################

# if not APP.first_site:
#     del pcmh_0_credit_card

request.nav = Navigator()


def index():
    pcmh = int(request.args(0) or 0)
    url = request.nav[pcmh]['index']
    redirect(url)


def download():
    return response.download(request, db)

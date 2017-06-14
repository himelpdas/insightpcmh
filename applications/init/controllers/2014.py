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

response.view = os.path.join("templates", "survey_2014.html")  # http://stackoverflow.com/questions/8750723/is-it-possible-to-change-a-web2py-view-on-the-fly

# IS_SINGLE_OR_LARGEST_CORPORATE = (APP.application_size == "Single") or APP.largest_practice

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

        db(db.application.id == APP_ID).update(progress='{:.1%}'.format(self.numerator/self.denominator))

    def init_title(self):
        if self.get_pcmh_from_request():
            pcmh = self.get_pcmh_from_request()
            label = self[pcmh]['elements'][self.get_element_from_request()]["label"]
            response.title = "PCMH ({pcmh}) {title} - {label}".format(pcmh=pcmh,
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


# (0)###################################################


# def pcmh_0_credit_card():
#     """Credit Card (To Purchase NCQA Tools)"""
#     cc = CryptQNA(
#         1, 1,
#         True,
#         'credit_card',
#         "Please enter your credit card in order to purchase the ISS survey tool. The NCQA store accepts American "
#         "Express, Discover, Master Card and Visa."
#     )
#     cc.set_template(
#         "{gpg_encrypted}")
#     return dict(documents={})


def pcmh_0_emr():
    """Electronic Medical Record Info"""

    if APP.emr in CLOUD_EMRS:
        db.emr_login.website.requires = IS_URL()

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

    # emr_credentials = CryptQNA(
    #     1, float("inf"),  # change the 3 to the number of days the practice is open from the info
    #     getattr(account_created.row, "please_choose", None) == "Yes",
    #     'emr_credentials',
    #     "Please provide the username and password to the {emr} account that was created for "
    #     "Insight Management.".format(emr=APP.emr),
    # )
    #
    # emr_credentials.set_template(
    #     "{gpg_encrypted}")

    emr_login = MultiQNA(
        1, float("inf"),  # change the 3 to the number of days the practice is open from the info
        getattr(account_created.row, "please_choose", None) == "Yes",
        'emr_login',
        "Please provide the username and password to the {emr} account that was created for "
        "Insight Management.".format(emr=APP.emr),
    )

    emr_login.set_template("Site: {website} <br>User: {username}<br>Password: {password}")

    return dict(documents={})

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
#     return dict(documents={})


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
                 URL('static', 'pcmh/practice_fusion/same_day_appointment_setting.png')),
                ("2. Repeat", "Repeat this for every day your practice is open. "
                              "You need at least one 15-minute block per day.",
                 URL('static', 'pcmh/practice_fusion/same_day_appointment_set.png'))
            ])
        )
    )

    same_day_blocks = MultiQNA(
        len(block_days), float("inf"),  # change the 3 to the number of days the practice is open from the info
        getattr(same_day_appointments.row, "please_choose", None) == "Yes",
        'same_day_block',
        "Enter your same-day appointment blocks.",
        validator=_validate_start_end_time,
    )

    same_day_blocks.set_template("{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                 "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}")

    same_day_block_rows = db(db.same_day_block.application == APP_ID).select()

    if len(same_day_block_rows) >= len(block_days):
        diff = set(map(lambda e: e.day_of_the_week, same_day_block_rows)).symmetric_difference(block_days)
        same_day_blocks.add_warning(diff, "You are missing same-day block(s) for %s." % ", ".join(sorted(diff)))

    return dict(documents={
        # ("PCMH_1A_4.doc", URL("init", "policy", "PCMH_1A_4.doc"))
    })


def pcmh_1_1a__2():
    """After hours"""

    extra = "<small>For example, in an office with typical business hours from 9AM - 5PM, " \
            "the following examples are considered extended business hours for seeing patients:" \
            "<ul><li>Monday - Thursday 9AM - 5PM, Friday 10AM - 6PM (shift in hours for one day of the week)</li>" \
            "<li>Monday - Thursday 9AM - 5PM, Friday 9AM - 6PM (extra hours for one day of the week)</li>" \
            "<li>Monday - Friday 9AM - 5PM, Saturday 9AM - 3PM (extra day during a weekend)</li>" \
            "</ul></small>"

    after_hours = MultiQNA(
        1, 1, True,
        'after_hours',
        "Does the practice see patients outside regular business hours?"
    )

    after_hours.set_template("{please_choose}")

    after_hours.add_warning(
        getattr(after_hours.row, "please_choose", None) in NOT_YES,
        "In order to get credit for PCMH 1A2, the practice must see patients during extended business hours at least "
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

    return dict(documents={})


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

    return dict(documents={})


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
                  "Arrival\"", URL('static', 'pcmh/practice_fusion/mark_as_no_show.png' ))]
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

    return dict(documents={})


# (1b)###################################################\
def pcmh_1_1b__1_2_3_4():
    """Clinical advice (telephone encounters)"""

    telephone_encounter_table_url = URL('init', 'word', 'telephone_log.doc',
                                        vars=dict(type="meeting", **request.get_vars),
                                        hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"])

    telephone_encounter = MultiQNA(
        1, 1,
        True,
        'telephone_encounter',
        "Does {practice} use <a href='{url}'>this telephone encounter log</a> (or an equivalent system) to track "
        "<b>telephone encounters</b>? Does the practice document advice given to patients into the patient record?"
        .format(practice=APP.practice_name, url=telephone_encounter_table_url)
    )

    telephone_encounter.add_warning(
        getattr(telephone_encounter.row, "please_choose", None) in NOT_YES,
        "{practice} must keep a log of all telephone encounters and document advice given to patents into the patient "
        "record (refill requests alone do not satisfy the PCMH standard).{carousel}".format(
            practice=APP.practice_name,
            carousel=
            CAROUSEL(
                "telephone_encounter",
                [("1. Create Encounter",
                  "In the patient's chart, create a new encounter.",
                  URL('static', 'pcmh/practice_fusion/telephone_encounter_create2.png')),
                 ("2. Describe Encounter",
                  "Describe when the call was received, when the call was ended satisfied, and a summary of the call. "
                  "Note if patient expresses understanding of the advice given.",
                  URL('static', 'pcmh/practice_fusion/telephone_encounter_ex.png'))]
            )
        )
    )

    telephone_encounter.set_template("{please_choose}")

    telephone_encounter_log = MultiQNA(
        1, float("inf"),
        getattr(telephone_encounter.row, "please_choose", None) == "Yes",
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

    telephone_encounter_during_hours_example.set_template("{patient_name}: {patient_dob} {screenshot}")

    telephone_encounter_after_hours_example = MultiQNA(
        1, 1, telephone_encounter_log.rows,
        'telephone_encounter_after_hours_example',
        temp % (1, "", "after")
    )

    telephone_encounter_after_hours_example.set_template("{patient_name}: {patient_dob} {screenshot}")

    return dict(documents={})


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
#     return dict(documents={})


# (2)###################################################
def pcmh_2_2d__1_2():
    """Team Structure"""

    providers = MultiQNA(
        1, float("inf"),
        True,
        'provider',
        "Please enter your staff who <b>are</b> providers.",
    )

    days = providers
    providers.set_template(
        "<b class='text-success'>{first_name} {last_name}, "
        "{role}<br>&emsp;Usually in office on: {days_of_the_week}</b>")

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
        "{first_name} {last_name}, {role}&emsp;Usually in office on: {days_of_the_week}")

    # providers = db(db.provider.application == APP_ID).count()
    #
    # assigned_pcp = MultiQNA(
    #     1, 1, providers > 1,
    #     'assigned_pcp',
    #     "Is the patient's preferred clinician documented in his/her patient record?"
    # )
    #
    # assigned_pcp.set_template("{please_choose}")
    #
    # assigned_pcp.add_warning(
    #     getattr(assigned_pcp.row, "please_choose", None) in NOT_YES,
    #     "In a multi-PCP setting, the practice should document the patient's PCP into the patient record in order to "
    #     "receive credit for PCMH 2A."
    # )
    #
    # see_assigned_pcp = MultiQNA(
    #     1, 1, getattr(assigned_pcp.row, "please_choose", None) == "Yes",
    #     'see_assigned_pcp',
    #     "Do patients get to see their assigned PCP at least 75% of the time?"
    # )
    #
    # see_assigned_pcp.add_warning(
    #     getattr(see_assigned_pcp.row, "please_choose", None) in NOT_YES,
    #     "In a multi-PCP setting, the pactice should implement a policy to allow patients to see their assigned PCP in "
    #     "order to receive credit for PCMH 2A."
    # )
    #
    # see_assigned_pcp.set_template("{please_choose}")

    return dict(documents={})


def pcmh_2_2d__3_5_6_7_8():
    """Huddles, Meetings & Trainings"""

    huddle_sheet_url = URL('init', 'word', 'huddle_sheet.doc', vars=dict(**request.get_vars), hmac_key=MY_KEY,
                           salt=session.MY_SALT, hash_vars=["app_id"])

    # referral tracking chart
    huddle_sheet = MultiQNA(
        1, float('inf'), True,
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

    return dict(documents={})


# (3)###################################################

def pcmh_3_3a__1_2_3_4_5_6_7_9_10_11_12_13_14():
    """Patient Demographics"""

    patient_demographics_choices = ['Date of birth', 'Sex', 'Race', 'Ethnicity', 'Preferred language',
                                    'Telephone numbers', 'E-mail address', 'Occupation',
                                    'Dates of previous clinical visits', 'Legal guardian/health care proxy',
                                    'Primary caregiver', 'Presence of advance directives',
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
        "Which of the following demographic fields does %s record?" % APP.practice_name
    )

    choices = getattr(patient_demographics.row, "please_choose", None)

    if choices:
        patient_demographics.add_warning(
            len(choices) < minimum,
            "{pc} needs to be able to record <b>at least {min}</b> of these choices (only {max}/{min} picked): "
            "{li} Please fill out more of these fields for your new and recent patients. Then "
            "come back and change your answer.".format(pc=APP.practice_name, min=minimum, max=len(choices),
                                                       li=OL(*map(lambda e: LI(e), patient_demographics_choices)))
        )

    patient_demographics.set_template("{please_choose}")
    return dict(documents={})


def pcmh_3_3d__1_2_3_4_5():
    """Patient callback"""

    callback_list = MultiQNA(
        1, float("inf"), True,
        'callback_list',
        "Please upload callback lists for <b>2 vaccinations/immunizations, 2 preventative care services, "
        "3 chronic/acute services, overdue visit and medication monitoring (i.e. Coumadin)</b>. Logs can be sourced "
        "from {emr}, QARR/HEDIS (from 3 or more health plans), and/or CIR recall lists. Documents must be dated "
        "within the last 10 months."
        "".format(emr=APP.emr)
    )

    callback_list.set_template("{choose_file}")

    return dict(documents={})

# (4)###################################################


def pcmh_4_4b__1_2_3_4_5___3e__1_2_3_4_5():
    """Care plans"""

    is_pediatrics = APP.practice_specialty == "Pediatrics"

    care_plan = MultiQNA(
        1, 1, True, "care_plan",
        ("For <b>every care plan</b>, does {practice} thoroughly discuss or assess <b>all</b> of the following? "
         "<small><ul><li>Prescription and OTC risk / reward / usage / understanding</li>"
         "<li>Patient goals / preferences / life-style</li>"
         "<li>Patient barriers to maintaining treatment plan or medications</li>"
         "<li>labs / screenings / referrals ordered</li>"
         "<li>Resources or materials given to patient or family</li>"
         "<li>Recent hospitalizations or self-referrals</li>%s</small>" %
         (" " if is_pediatrics else "<li>Advanced care planning</li>")
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
        "patient. Patient acknowledged understanding of prescribed medications and treatment care plan.</li></ul?>"
        % ("" if is_pediatrics else "<li>Describe the discussion of advanced care planning with the patient.</li>")
    )

    for _each in MEASURES_3E:
        measure = MultiQNA(
            1, float("inf"), care_plan.row,
            _each[0],
            "Please provide a patient with a detailed evidence-based care plan for <b>{measure_description}</b>. "
            .format(measure_description=_each[1])
        )

        measure.set_template("{patient_name}: {patient_dob}<br>Serviced on: {service_date} {screenshot}")

    return dict(documents={})

# (5)###################################################


def pcmh_5_5a__1_2_3_4_5_6___5b__5_6_8():
    """Lab, Image, Referral Tracking & Follow-Up"""
    temp = "Does {practice} use <a href='{table_url}'>this {order_type} tracking table</a> (or an equivalent system) " \
           "to track <b>{order_type} orders</b>?"
    _imaging = "imaging (X-Ray, MRI, Sonogram, EKG etc.)"

    # image tracking
    image_table_url = URL('init', 'word', 'tracking_chart.doc', args=["image_order_tracking_chart"],
                          vars=dict(type="image", **request.get_vars),
                          hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"])
    image_tracking = MultiQNA(
        1, 1, True,
        'image_tracking', temp.format(
            practice=APP.practice_name, order_type=_imaging, table_url=image_table_url)
    )
    image_tracking.set_template("{please_choose}")

    # lab tracking
    lab_table_url = URL('init', 'word', 'tracking_chart.doc', args=["lab_order_tracking_chart"],
                        vars=dict(type="lab", **request.get_vars),
                        hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"])
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
    referral_tracking = MultiQNA(
        1, 1, True,
        'referral_tracking', temp.format(
            practice=APP.practice_name, order_type="referral", table_url=referral_table_url)
    )
    referral_tracking.set_template("{please_choose}")

    temp = "{practice} should use <a href='{chart_url}'>this table</a> (or an equivalent tracking system) to track " \
           "{order_type} orders to best meet PCMH requirements"

    image_tracking.add_warning(
        getattr(image_tracking.row, "please_choose", None) in NOT_YES,
        temp.format(practice=APP.practice_name, chart_url=image_table_url, order_type=_imaging)
    )
    
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

    # image tracking chart
    image_tracking_chart = MultiQNA(
        1, float('inf'), image_tracking.row,
        'image_tracking_chart',
        temp.format(order_type=_imaging)
    )

    image_tracking_chart.set_template("{choose_file}")

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

    # lab follow up
    lab_follow_up = MultiQNA(
        1, 1, lab_tracking.row,
        'lab_follow_up', temp % "lab")

    lab_follow_up.set_template("{please_choose}")

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

    lab_follow_up.add_warning(
        getattr(lab_follow_up.row, "please_choose", None) in NOT_YES,
        temp % "lab")

    image_follow_up.add_warning(
        getattr(image_follow_up.row, "please_choose", None) in NOT_YES,
        temp % _imaging)
    
    referral_follow_up.add_warning(
        getattr(referral_follow_up.row, "please_choose", None) in NOT_YES,
        temp % "referral")

    temp = "Please provide 3 patients where {practice} created a telephone encounter " \
           "or letter to the patient regarding <b>%s</b> in the patient's record.".format(practice=APP.practice_name)

    # lab follow up example normal
    lab_follow_up_normal_example = MultiQNA(
        3, float('inf'), getattr(lab_follow_up.row, "please_choose", None) == "Yes",
        'lab_follow_up_normal_example', temp % "normal lab results"
        )

    lab_follow_up_normal_example.set_template("{patient_name}: {patient_dob}")

    # lab follow up example abnormal
    lab_follow_up_abnormal_example = MultiQNA(
        3, float('inf'), getattr(lab_follow_up.row, "please_choose", None) == "Yes",
        'lab_follow_up_abnormal_example', temp % "abnormal lab results")

    lab_follow_up_abnormal_example.set_template("{patient_name}: {patient_dob}")

    # image follow up example normal
    image_follow_up_normal_example = MultiQNA(
        3, float('inf'), getattr(image_follow_up.row, "please_choose", None) == "Yes",
        'image_follow_up_normal_example', temp % "normal imaging results")

    image_follow_up_normal_example.set_template("{patient_name}: {patient_dob}")

    # image follow up example abnormal
    image_follow_up_abnormal_example = MultiQNA(
        3, float('inf'), getattr(image_follow_up.row, "please_choose", None) == "Yes",
        'image_follow_up_abnormal_example', temp % "abnormal imaging results")

    image_follow_up_abnormal_example.set_template("{patient_name}: {patient_dob}")

    # referral follow up example normal
    referral_follow_up_normal_example = MultiQNA(
        3, float('inf'), getattr(referral_follow_up.row, "please_choose", None) == "Yes",
        'referral_follow_up_normal_example', temp % "normal referral results"
        )

    referral_follow_up_normal_example.set_template("{patient_name}: {patient_dob}")

    # referral follow up example abnormal
    referral_follow_up_abnormal_example = MultiQNA(
        3, float('inf'), getattr(referral_follow_up.row, "please_choose", None) == "Yes",
        'referral_follow_up_abnormal_example', temp % "abnormal referral results")

    referral_follow_up_abnormal_example.set_template("{patient_name}: {patient_dob}")

    # todo - add new born screening for peds

    return dict(documents={})


def pcmh_5_5b__1_2_3_5_6_7_8_9_10():
    """Care Coordination"""

    temp = "Please upload a copy of a referral order to a <b>%s</b> that includes the latest patient " \
           "demographics (i.e. latest care plan, medications, etc.), the latest lab/screening/test results and the " \
           "following informal agreement.<small><p><ul><li>In referring this patient to your care, {practice} expects "\
           "in return a full report regarding our patient’s visit within 7 days of the appointment. Additionally, " \
           "please send any documentation regarding your diagnosis and any treatment options considered. If you " \
           "have any questions please contact our office.</small></li></ul>".format(practice=APP.practice_name)

    psych_order_example = MultiQNA(
        1, 1, True,
        'psych_order_example', temp % "psychiatrist"
    )

    psych_order_example.set_template("{choose_file}")

    specialist_order_example = MultiQNA(
        1, 1, True,
        'specialist_order_example', temp % "specialist"
    )

    specialist_order_example.set_template("{choose_file}")

    return dict(documents={})


def pcmh_5_5c__3():
    """ER/IP discharge log"""
    er_ip_log_url = URL('init', 'word', 'er_ip_log.doc',
                        vars=dict(**request.get_vars),
                        hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"])
    # er_ip_log tracking chart
    er_ip_log = MultiQNA(
        1, float('inf'), True,
        'er_ip_log',
        "Please fill out this <a href='{url}'>ER/IP log</a> with at least 4 months of past data. Continue to maintain "
        "this log permanently as part of your PCMH transformation. <b>Please make sure all the patients in this log "
        "have their discharge summary in their patient record!</b>"
        .format(url=er_ip_log_url)
    )

    er_ip_log.set_template("{choose_file}")

    return dict(documents={})


# (6)###################################################
def pcmh_6_6a__1_2_3_4():
    """Performance reports"""
    report_cards = MultiQNA(
        1, float("inf"), True,
        'report_card',
        "Please upload QARR/HEDIS performance report cards from a <b>minimum of 3 health plans</b> (i.e. Health First, "
        "Fidelis, etc.) <b>Alternatively</b>, you may upload reporting from {emr} showing performance of "
        "<b>two immunization measures</b>, <b>two preventative care measures</b> and <b>two chronic care measures.</b> "
        "Documents must be dated no older than 10 months.".format(emr=APP.emr)
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

    return dict(documents={})

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

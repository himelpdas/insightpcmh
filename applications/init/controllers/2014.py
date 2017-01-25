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

IS_SINGLE_OR_LARGEST_CORPORATE = (APP.application_size == "Single") or APP.largest_practice


class Navigator:
    titles = ["Practice", "Access", "Team", "Population", "Care", "Coordination", "Performance"]

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
        if request.reuse:
            QNA.instances = [request.reuse]

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
        print self.all_questions
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

                label = element.capitalize().replace("__", " → ").replace("_", ", ")

                is_complete = self.function_is_complete(func)
                icon = SPAN(_class="glyphicon glyphicon-%s text-%s" %
                                   ("ok" if is_complete else "remove",
                                    "success" if is_complete else "danger")
                            )

                description = SPAN(icon, " ", func.__doc__) if pcmh == 0 else \
                    SPAN(icon, plural, label, ": ", func.__doc__)

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


def pcmh_0_credit_card():
    """Credit Card (To Purchase NCQA Tools)"""
    if IS_SINGLE_OR_LARGEST_CORPORATE:
        cc = CryptQNA(
            1, 1,
            True,
            'credit_card',
            "Please enter your credit card in order to purchase the ISS survey tool. The NCQA store accepts American "
            "Express, Discover, Master Card and Visa."
        )
        cc.set_template(
            "{gpg_encrypted}")
    else:
        response.flash="Enter credit card in the largest practice's portal!"
    return dict(documents={})


def pcmh_0_hours():
    """Office hours"""
    office_hours = MultiQNA(
        3, float("inf"),
        True,
        'office_hours',
        "What are the practice's office hours? Note, these must be hours when <span class='dashed-underline'>patients "
        "are seen</span>.",
        validator=_validate_start_end_time,
    )

    office_hours.set_template("{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}")

    return dict(documents={})


def pcmh_0_staff():
    """Practice Staff"""
    providers = MultiQNA(
        1, float("inf"),  # change the 3 to the number of days the practice is open from the info
        True,
        'billing_provider',
        "Enter your providers here.",
    )

    days = providers
    providers.set_template(
        "<b class='text-success'>{first_name} {last_name}, {role}<br>&emsp;Usually in office on: {days_of_the_week}</b>")

    has_staff = MultiQNA(
        1, 1,
        True,
        'has_staff',
        "Aside from yourself and other providers, do you have any other staff or non-billing providers (i.e. PAs, MAs, "
        "front desk, office manager, etc.)?"
    )

    has_staff.set_template(
        "{please_choose}")

    staff = MultiQNA(
        1, float("inf"),  # change the 3 to the number of days the practice is open from the info
        getattr(has_staff.row, "please_choose", None) == "Yes",
        'staff',
        "You said you have other staff and/or non-billing providers. Enter them here.",
    )

    staff.set_template(
        "{first_name} {last_name}, {role}&emsp;Usually in office on: {days_of_the_week}")

    return dict(documents={})


def pcmh_0_emr():
    """Electronic Medical Record Info"""

    account_created = MultiQNA(
        1,1,
        True,
        'account_created',
        "Insight Management requires access to <i>%s</i> via a login that has provider or admin level access. "
        "Do you have this login information ready?" % APP.emr if APP.emr != "Other" else "the EMR"
    )

    account_created.set_template(
        "{please_choose}")

    account_created.add_warning(getattr(account_created.row, "please_choose", None) in NOT_YES,
                                XML(T(
                                    "Please create provide an account that has provider or admin level access, then "
                                    "come back and change your answer.")))

    emr_credentials = CryptQNA(
        1, float("inf"),  # change the 3 to the number of days the practice is open from the info
        getattr(account_created.row, "please_choose", None) == "Yes",
        'emr_credentials',
        "Please provide the username and password to the account. If there are more than one credential <i>(i.e. login "
        "for computer, login for EMR app, etc.)</i>, then add them all here along with a small description in the note "
        "field.",
    )

    emr_credentials.set_template(
        "{gpg_encrypted}")

    return dict(documents={})

def pcmh_0_ncqa():
    """NCQA logins"""
    application = CryptQNA(
        1, 1,
        True,
        'ncqa_app',
        "Enter the login information for the application tool."
    )
    application.set_template(
        "{gpg_encrypted}")

    iss = CryptQNA(
        1, 1,
        True,
        'ncqa_iss',
        "Enter the login information for the ISS survey tool."
    )
    iss.set_template(
        "{gpg_encrypted}")

    return dict(documents={})


# (1a)###################################################

def pcmh_1_1a__2():
    """After hours"""

    extra = "<br><br><small> The following examples are considered extended buisiness hours: <ul>" \
            "<li>Monday - Thursday 9AM - 5PM, Friday 10AM - 6PM (shift in hours)</li>" \
            "<li>Monday - Thursday 9AM - 5PM, Friday 9AM - 6PM (extra hours)</li>" \
            "<li>Monday - Friday 9AM - 5PM, Saturday 9AM - 3PM (weekend hours)</li>" \
            "</ul></small>"

    after_hours = MultiQNA(
        1, 1, True,
        'after_hours',
        "Does the practice have any extended office hours (hours when patients are seen), <u>at least</u> once a week?"+
        extra
    )

    after_hours.set_template("{please_choose}")

    after_hours.add_warning(
        getattr(after_hours.row, "please_choose", None) in NOT_YES,
        "In order to get credit for PCMH 1A2, the practice must see patients during extended buisiness hours at least "
        "once a week. Please note, that this does not include the provider \"staying late\" on some days; this must be "
        "implemented as a policy of the practice."
    )

    after_hour_blocks = MultiQNA(
        1, float("inf"),
        getattr(after_hours.row, "please_choose", None) == "Yes",
        'after_hour_block',
        "You said you have extended hours. Please enter your extended hours here.",
        validator=_validate_start_end_time,
    )

    after_hour_blocks.set_template("{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                   "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}")



    return dict(documents={})


def pcmh_1_1a__1():
    """Same Day Appointments"""

    sda_example = "Please see <a href='{url}'>these examples</a> " \
                  "of ideal same-day scheduling.".format(
        url=URL('init', 'word', 'same_day_training_generic.xml',
                vars=request.get_vars,
                hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"]))

    same_day_appointments = MultiQNA(
        1, 1, True,
        'same_day_appointments',
        "Does the practice visibly reserve time on the scheduler <span class='dotted-underline'>every day</span> "
        "for same-day appointments? " + sda_example
    )

    same_day_appointments.set_template("{please_choose}")

    same_day_appointments.add_warning(
        getattr(same_day_appointments.row, "please_choose", None) in NOT_YES,
        "The practice <b>MUST</b> reserve time every day that patients are seen for same-day appointments. It "
           "is a requirement for PCMH certification at any level. We recommend at least two 15 minute slots reserved "
           "visibly in your scheduler, for <u>each day patients are seen</u>. " + sda_example
    )

    same_day_blocks = MultiQNA(
        3, float("inf"),  # change the 3 to the number of days the practice is open from the info
        getattr(same_day_appointments.row, "please_choose", None) == "Yes",
        'same_day_block',
        "Enter your same-day time blocks. You must have same-day blocks for each day your practice sees patients.",
        validator=_validate_start_end_time,
    )

    same_day_blocks.set_template("{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                 "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}")


    walkin = MultiQNA(
        1, 1,
        getattr(same_day_appointments.row, "please_choose", None) == "Yes",
        'walkin',
        "Aside from same-day appointments, are you mainly a walk-in clinic?"
    )

    walkin.set_template("{please_choose}")

    next_available_appointments = MultiQNA(
        1, float("inf"),
        getattr(walkin.row, "please_choose", None) in NOT_YES,
        'next_available_appointment',
        "Aside from same-day appointments, what are your other appointment types and how long until their next available appointments?",
    )

    next_available_appointments.set_template("{appointment_type} available within {available_within} {unit}")

    return dict(documents={
        ("PCMH_1A_4.doc", URL("init", "policy", "PCMH_1A_4.doc"))
    })



def pcmh_1_1a__4():
    """Availability of appointments"""

    same_day_appointments = MultiQNA(
        1, 1, True,
        'availability_of_appointments',
        "What is the practice's availability for the following appointment types?"
    )

    return dict(documents={})


def pcmh_1_1a__5():
    """Monitoring no-shows"""
    no_shows_training = MultiQNA(
        1, 1, True,
        'no_shows_training',
        "Does the practice actively contact no-show patients?"
    )

    no_shows_training.add_warning(
        getattr(no_shows_training.row, "please_choose", None) in NOT_YES,
        ("The practice must begin monitoring patient no-shows <b>as soon as possible</b>. No-shows are calculated by "
         "measuring the ratio of patients who arrived for their appointment (numerator) to the total number of patients"
         " scheduled for any appointment for a given time period. NCQA requires a no-show report spanning for at "
         "least 30 days. Please see <a href=''>this guide</a> to see how to do this with your EMR.").format(url=None)
    )

    no_shows_training.set_template("{please_choose}")

    no_show_emr = MultiQNA(
        1, 1,
        getattr(no_shows_training.row, "please_choose", None) == "Yes",
        'no_show_emr',
        "When a patient does not show up for his/her appointment, do you mark that appointment as a missed appointment "
        "/ no-show?"
    )

    no_show_emr.set_template("{please_choose}")

    return dict(documents={})

# (1b)###################################################

def pcmh_1_1b__1_2_3_4():
    """Clinical advice (calls and messages)"""
    answering_service = MultiQNA(
        1, 1,
        True,
        'answering_service',
        "How does <i>%s</i> handle after-hour incoming telephone encounters for medical advice?" % APP.practice_name
    )

    answering_service.set_template("{please_choose}")

    telephone_encounter = MultiQNA(
        1, 1,
        True,
        'telephone_encounter',
        "With regard to incoming telephone encounters, does <i>%s</i> record all of the following "
        "into the <b>patient record</b> during and after business hours?<small><ol>"
        "<li>A summarized transcript of the <b>advice</b> given to the caller.</li>"
        "<li>The time and date when the call was answered by the practice.</li>"
        "<li>The time and date when the caller received a response.</li>"
        "</ol></small>" % APP.practice_name
    )

    telephone_encounter.add_warning(
        getattr(telephone_encounter.row, "please_choose", None) in NOT_YES,
        "In order to receive credit for the entire PCMH 1B section, <i>%s</i> must record all incoming telephone "
        "encounters (during and after business hours) regarding clinical advice (refill requests "
        "do not count) into the patient record. See <a href=#>these examples</a> of  good telephone encounters."
        % APP.practice_name
    )

    telephone_encounter.set_template("{please_choose}")

    telephone_encounter_examples = MultiQNA(
        3, 3, getattr(telephone_encounter.row, "please_choose", None) == "Yes",
        'telephone_encounter_examples',
        "Please provide <b>3 patient names</b> where the telephone encounter was documented in the "
        "<span class='dashed-underline'>same week</span>. The examples <span class='dashed-underline'>must</span> be regarding clinical advice, "
        "<span class='dashed-underline'>not</span> refill requests!"
    )

    telephone_encounter_examples.set_template("{patient_name}: {patient_dob}")

    return dict(documents={})


def pcmh_1_1c__1_2_3_4_5_6():
    """Meaningful use"""
    meaningful_use = MultiQNA(
        1, float("inf"),
        True,
        'meaningful_use',
        "Please upload a meaningful use report no more than 6 months old."
    )

    meaningful_use.set_template("{choose_file}")

    return dict(documents={})

# (2)###################################################

def pcmh_2_2b__3_4():
    """Transition of Care"""

    transition_of_care_plan_internal = MultiQNA(
        1, 1, True,
        'transition_of_care_plan_internal',
        "Does the practice have a transition of care plan for importing a patient from pediatric care?"
    )

    transition_of_care_plan_internal.add_warning(
        getattr(transition_of_care_plan_internal.row, "please_choose", None) in NOT_YES,
        "Please schedule a training session with your trainer. Change your answer after training."
    )

    transition_of_care_plan_internal.set_template("{please_choose}")

    intake_form = MultiQNA(
        1, 1, getattr(transition_of_care_plan_internal.row, "please_choose", None) == "Yes",
        'intake_form',
        "Do you have an intake form for transitioning a pediatric patient into your practice?"
    )

    intake_form.set_template("{please_choose}")

    intake_form.add_warning(
        getattr(intake_form.row, "please_choose", None) in NOT_YES,
        "Please download this {intake_form_url} and customize it. Change your answer when you're done".format(
            intake_form_url=A("template", _href=URL("policy", "ADHD_screening_letter.doc"))
        )
    )

    intake_form_upload = MultiQNA(
        1, False,
        getattr(intake_form.row, "please_choose", None) == "Yes",
        'intake_form_upload',
        "You said you have an intake form. Please upload a copy of this intake form here.",
        validator=_on_validation_filename,
    )

    intake_form_upload.set_template("<a href='%s'>{filename}</a>" % URL('download', args="{upload}",
                                                                               url_encode=False))  # encode escapes {}

    intake_form_patient_example = MultiQNA(
        3, False,
        getattr(intake_form.row, "please_choose", None) == "Yes",
        'intake_form_patient_example',
        "Enter <u>3 or more</u> patient names where each patient has a completed intake form in the patient record.",
    )

    intake_form_patient_example.set_template("{patient_first_name} {patient_last_name}, "
                                             "{patient_DOB}")

    return dict(documents={})

# (2)###################################################

def pcmh_2_2a__1():
    """Assigned PCP"""

    providers = db((db.billing_provider.id > 0) & (db.application.id == APP_ID)).count()

    assigned_pcp = MultiQNA(
        1, 1, True,
        'assigned_pcp',
        "Is the patient's preferred clinician documented in his/her patient record? <a href=#>See example.</a>"
    )

    assigned_pcp.set_template("{please_choose}")

    assigned_pcp.add_warning(
        not providers,
        "It is highly recommended that you enter <b>all</b> of your providers in "
        "<a href='%s'>section 0</a> before answering this question." % URL("init", "2014", "pcmh_0_staff",
                                                                           args=request.args, vars=request.get_vars)
    )

    assigned_pcp.add_warning(
        getattr(assigned_pcp.row, "please_choose", None) in NOT_YES,
        "In a multi-PCP setting, the practice should document the patient's PCP into the patient record in order to "
        "receive credit for PCMH 2A."
    )

    see_assigned_pcp = MultiQNA(
        1, 1, getattr(assigned_pcp.row, "please_choose", None) == "Yes",
        'see_assigned_pcp',
        "Do patients get to see their assigned PCP at least 75% of the time?"
    )

    see_assigned_pcp.add_warning(
        getattr(see_assigned_pcp.row, "please_choose", None) in NOT_YES,
        "In a multi-PCP setting, the pactice should implement a policy to allow patients to see their assigned PCP in "
        "order to receive credit for PCMH 2A."
    )

    see_assigned_pcp.set_template("{please_choose}")

    return dict(documents={})

# (3)###################################################
def pcmh_3_3b__1_4b__1_4c__1():
    """Record Review Workbook"""
    return dict(documents={})

def pcmh_3_3a__1_2_3_4_5_6_7_9_10_11_12_13_14():
    """Patient Demographics"""

    patient_demographics_choices = ['Date of birth', 'Sex', 'Race', 'Ethnicity', 'Preferred language', 'Telephone numbers', 'E-mail address', 'Occupation', 'Dates of previous clinical visits', 'Legal guardian/health care proxy', 'Primary caregiver', 'Presence of advance directives', 'Health insurance information', 'Name and contact information of other health care professionals involved in patient\'s care.']
    minimum = 10

    if APP.practice_specialty == "Pediatrics":
        patient_demographics_choices = filter(lambda t: t[0] not in [7, 9], patient_demographics_choices)
        minimum = 8

    db.patient_demographics.please_choose.requires = IS_IN_SET(patient_demographics_choices, multiple=True)

    patient_demographics = MultiQNA(
        1, 1, True,
        'patient_demographics',
        ("Recording patient demographics <b>thoroughly</b> is considered good PCMH behavior. Which of the following "
         "information does <i>%s</i> record <b>at least 80%%</b> of the time with new patients?") % APP.practice_name
    )

    choices = getattr(patient_demographics.row, "please_choose", None)

    if choices:
        patient_demographics.add_warning(
            len(choices) < minimum,
            "<i>%s</i> needs to be able to meet <b>at least %s</b> of these choices (%s given): %s Please consider filling out "
            "more of these fields for your new and recent patients (need minimum 3 months of data). Then come back "
            "and change your answer." %
            (APP.practice_name, minimum, len(choices), TAG.SMALL(OL(*map(lambda e: LI(e), patient_demographics_choices))))
        )

    patient_demographics.set_template("{please_choose}")
    return dict(documents={})

def pcmh_3_3b__1_2_3_4_5_6_7_8_9_10_11():
    """Clinical Data (2014 Meaningful use)"""
    documents = {}

    meaningful_use = MultiQNA(
        1, float("inf"),
        True,
        'meaningful_use_2014',
        "If available in your EMR, please upload the <span class='dashed-underline'>Stage 1 Meaningful Use</span> "
        "report using the 2014 standards."
    )

    meaningful_use.set_template("{choose_file}")

    return dict(documents=documents)

# (4)###################################################
def pcmh_4_4a__1():
    """holder"""
    return dict(documents={})

# (5)###################################################
def pcmh_5_5a__1_3():
    """Lab Tracking"""
    lab_tracking_generic = MultiQNA(
        1, 1, True,
        'lab_tracking_generic',
        "<i>%s</i> needs to <b>track labs</b> until the lab center's report is available, "
        "while flagging and following up on overdue reports. Flagging abnormal results and notifying patients of normal"
        " and abnormal results are of importance as well. Please download <a href='%s'><b>this chart</b></a> "
        "and fill out a minimum of 5 days worth of orders. When you are done, scan (or take a picture) and upload the"
        " document below." % (
        APP.practice_name,
        URL('init', 'word', 'tracking_chart.doc', args=["lab_order_tracking_chart"],
            vars=dict(type="lab", **request.get_vars),
            hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"]))
    )

    lab_tracking_generic.set_template("{choose_file}")

    return dict(documents={})

def pcmh_5_5a__5_6():
    """Lab and Image Follow-Up"""
    lab_image_follow_up = MultiQNA(
        1, 1, True,
        'lab_image_follow_up',
        "Does <i>%s</i> contact patients when lab or imaging results arrive (regardless of abnormalities)? "
        "Is this contact recorded as a telephone encounter? Note, letters are acceptable as well, but a copy must be "
        "uploaded to the patient's documents." % (
            APP.practice_name
        )
    )

    lab_image_follow_up.set_template("{please_choose}")

    lab_image_follow_up.add_warning(
        getattr(lab_image_follow_up.row, "please_choose", None) in NOT_YES,
        "In order to get credit for PCMH 5A5, the practice must contact the patient for both lab and imaging results, "
        "and the contact must be recorded somewhere in the patient's record (i.e. as a telephone encounter)."
    )

    lab_image_follow_up_examples = MultiQNA(
        4, 4, getattr(lab_image_follow_up.row, "please_choose", None) == "Yes",
        'lab_image_follow_up_examples',
        "Please provide <b>4 patient names</b> where the patient was contacted about lab or "
        "imaging results (within the last 6 months). One must regard labs, one must regard imaging, "
        "one must regard abnormal results and one must regard normal results."
    )

    lab_image_follow_up_examples.set_template("{patient_name}: {patient_dob}")

    # todo - add new born screening for peds

    return dict(documents={})


def pcmh_5_5a__2_4():
    """Image Tracking"""
    image_tracking_generic = MultiQNA(
        1, 1, True,
        'image_tracking_generic',
        "<i>%s</i> needs to <b>track imaging</b> (EKGs, X-Rays, MRIs, etc.) until the imaging center's report is available, "
        "while flagging and following up on overdue reports. Flagging abnormal results and notifying patients of normal"
        " and abnormal results are of importance as well. Please download <a href='%s'>this chart</a> "
        "and fill out a minimum of 5 days worth of orders. When you are done, scan (or take a picture) and upload the"
        " document below." % (
            APP.practice_name,
            URL('init', 'word', 'tracking_chart.doc', args=["image_order_tracking_chart"],
                vars=dict(type="image", **request.get_vars),
                hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"]))
    )

    image_tracking_generic.set_template("{choose_file}")

    return dict(documents={})


def pcmh_5_5b__1_2_3_5_6_7_8_9_10():
    """Referral Tracking"""

    referral_blurb = MultiQNA(
        1, 1, True,
        'referral_blurb',
        "For <b>every referral sent</b>, an informal <span class='dashed-underline'>time-frame</span> and <span class='dashed-underline'>expectation of content</span> should be "
        "given to the specialist. <i>{practice}</i> should include or template the following text to all outgoing referrals (customize as you wish): "
        "<p><small><i>In referring this patient to your care, {practice} expects in return a full report "
        "regarding our patient’s visit <span class='dashed-underline'>within 7 days</span> of the appointment. Additionally, please send <span class='dashed-underline'>any documentation</span> regarding your diagnosis and <span class='dashed-underline'>any test, labs or "
        "imaging</span> you deem appropriate.</i></small></p> Are you including this text with every referral order?".format(practice=APP.practice_name)
    )

    referral_blurb.set_template("{please_choose}")

    referral_blurb.add_warning(getattr(referral_blurb.row, "please_choose", None) in NOT_YES,
                               "PCMH 5B is a must pass element, please consider correcting this answer."
                               )

    referral_tracking_generic = MultiQNA(
        1, 1, True,
        'referral_tracking_generic',
        "<i>%s</i> needs to <b>track referrals</b> until the consultant or specialist’s report is available, "
        "while flagging and following up on overdue reports. Please download <a href='%s'>this chart</a> "
        "and fill out a minimum of 5 days worth of referrals. When you are done, scan (or take a picture) and upload the"
        " document below." % (APP.practice_name,
                              URL('init', 'word', 'tracking_chart.doc', args=["referral_order_tracking_chart"],
                                  vars=dict(type="referral", **request.get_vars),
                                  hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"]))
    )

    referral_tracking_generic.set_template("{choose_file}")

    return dict(documents={})


def pcmh_5_5c__3():
    """Hospital discharge"""
    discharge_poster_url = URL('init', 'word', 'discharge_poster.doc',
                               vars=request.get_vars, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"])

    discharge_poster = MultiQNA(
        1, 1, True,
        'discharge_poster',
        "Does <i>%s</i> display (in the waiting room) <a href='%s'>this poster</a> (or any similar "
        "poster) that requests patients to inform the practice if they have been recently hospitalized?" %
        (APP.practice_name, discharge_poster_url)
    )

    discharge_poster.set_template("{please_choose}")

    discharge_poster.add_warning(getattr(
        discharge_poster.row, "please_choose", None) in NOT_YES,
                                   "<i>%s</i> must display <a href='%s'>this poster</a> (or similar)&mdash;"
                                   "visible in the waiting room&mdash;requesting that patients inform the practice"
                                   " if they have been recently hospitalized." %
                                   (APP.practice_name, discharge_poster_url)
                                   )

    return dict(documents={})


# (6)###################################################
def pcmh_6_6a__1_2_3():
    """QUARR/HEDIS"""

    qarr_hedis = MultiQNA(
        3, float("inf"), True,
        'qarr_hedis',
        "Upload QARR/HEDIS performance <span class='dashed-underline'>report cards</span> <b>and</b> the "
        "corresponding <span class='dashed-underline'>patient list for pending services</span> for a "
        "<span class='dashed-underline'>minimum of 3 health plans</span> "
        "<i>(i.e. Health First, Fidelis, etc.)</i>. Documents should be no older than 6 months."
    )

    qarr_hedis.set_template("{choose_file}")

    immunization_log = MultiQNA(
        1, float("inf"), True,
        'immunization_log',
        "Upload any CIR reports and/or immunization logs that <i>{pc}</i> may have. It is expected that the practice at the very "
        "least keeps a log of immunizations, whether or not <i>{pc}</i> conducts immunizations in-house."
        " Documents should be no older than 6 months.".format(pc=APP.practice_name)
    )

    immunization_log.set_template("{choose_file}")

    return dict(documents={})

# (end)###################################################

if not APP.largest_practice:
    del pcmh_0_credit_card
    # def pcmh_0_baa

request.nav = Navigator()


def index():
    pcmh = int(request.args(0) or 0)
    url = request.nav[pcmh]['index']
    redirect(url)


def download():
    return response.download(request, db)
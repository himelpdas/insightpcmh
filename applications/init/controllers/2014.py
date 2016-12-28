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
"""

from collections import OrderedDict

response.view = os.path.join("templates", "survey_2014.html")  # http://stackoverflow.com/questions/8750723/is-it-possible-to-change-a-web2py-view-on-the-fly

class Navigator:
    titles = ["Practice", "Access", "Team", "Population", "Care", "Coordination", "Performance"]

    def __init__(self):
        self.all_questions = List()
        # warning!! - function names MUST be sorted for init_list to work
        self.all_funcs = sorted(filter(lambda g: "pcmh_" == g[:5], globals()), key=lambda e: e.split("_", 2)[1])
        self.init_list()
        self.init_menu()

        if self.get_pcmh_from_request():
            pcmh = self.get_pcmh_from_request()
            description = self[pcmh]['elements'][self.get_element_from_request()]["description"]
            response.title = "PCMH ({pcmh}) {title} - {description}".format(pcmh=pcmh,
                                                                            title=self.get_title_from_pcmh(pcmh),
                                                                            description=description)

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
                (T('({pcmh}) {title}'.format(pcmh=each.pcmh, title=each.title)),
                 self.request_has_pcmh(each.pcmh),  # get element 1 without error
                 each.index, [])
            )

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

                label = element.capitalize().replace("_", " → ", 1).replace("_", ", ")
                assert func.__doc__, "missing doc strings for function %s" % func_name
                description = func.__doc__ if pcmh == 0 else "Element " + label + ": " + func.__doc__
                pcmh_dict = self.all_questions(pcmh)

                if not pcmh_dict:
                    pcmh_dict = Storage(pcmh=pcmh, done=False, index=URL('2014', func_name, vars=request.get_vars))
                    pcmh_dict["title"] = self.titles[pcmh]
                    pcmh_dict["elements"] = OrderedDict()
                    self.all_questions.append(pcmh_dict)

                element_dict = {element: Storage(description=description, element=element, func=func, done=False,
                                              url=URL('2014', func_name, vars=request.get_vars))}
                pcmh_dict["elements"].update(element_dict)


# (0)###################################################


def pcmh_0_credit_card():
    """Credit Card (To Purchase ISS Tool)"""
    cc = CryptQNA(
        1, 1,
        True,
        'credit_card',
        "Please enter your credit card in order to purchase the ISS survey tool. The NCQA store accepts American "
        "Express, Discover, Master Card and Visa."
    )
    cc.set_template(
        "{gpg_encrypted}")
    return dict(documents={})


def pcmh_0_hours():
    """Clinical hours"""
    clinical_hours = MultiQNA(
        3, float("inf"),
        True,
        'clinical_hour',
        "What are the practice's office hours? Only include days when patients are <u>actually seen</u>.",
        validator=_validate_start_end_time,
    )

    clinical_hours.set_template("{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}")

    """
    primary_contact = MultiQNA(
        1, 1,
        practice_info.row,
        'primary_contact',
        "Enter the primary contact who is able to handle all inquiries regarding this PCMH project."
    )

    primary_contact.set_template("{first_name} {last_name} ({role})<br>{email}<br>{phone} {extension}")
    """
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
    emr_name = MultiQNA(
        1, 1,
        True,
        'emr',
        "What is EMR that this practice uses?"
    )

    emr_name.set_template(
        "{name}")

    account_created = MultiQNA(
        1,1,
        emr_name.row,
        'account_created',
        "Insight Management requires access to <i>%s</i> via a login that has provider or admin level access. "
        "Do you have this login information ready?" % emr_name.row.name if emr_name.row else "the EMR"
    )

    account_created.set_template(
        "{please_choose}")

    account_created.add_warning(getattr(account_created.row, "please_choose", None) == "No",
                                XML(T(
                                    "Please create provide an account that has provider or amdmin level access, then "
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


# (1)###################################################


def pcmh_1_a_1():
    """Same Day Appointments"""

    same_day_appointments = MultiQNA(
        1, 1, True,
        'same_day_appointments',
        "Does the practice reserve time every clinical day for same-day appointments?"
    )

    same_day_appointments.set_template("{please_choose}")

    same_day_appointments.add_warning(
        getattr(same_day_appointments.row, "please_choose", None) == "No",
        "The practice <b>MUST</b> reserve time every day that patients are seen for same-day appointments. It "
           "is a requirement for PCMH certification at any level. We recommend at least two 15 minute slots reserved "
           "visibly in your scheduler, for <u>each day patients are seen</u>. Please see <a href='{url}'>these "
           "examples</a> of ideal same-day scheduling.".format(url=None)
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

    after_hours = MultiQNA(
        1, 1, True,
        'after_hours',
        "Does the practice have any after hours, <u>at least</u> once a week?"
    )

    after_hours.set_template("{please_choose}")

    after_hour_blocks = MultiQNA(
        1, float("inf"),
        getattr(after_hours.row, "please_choose", None) == "Yes",
        'after_hour_block',
        "You said you have after-hours. Please enter your after-hours here.",
        validator=_validate_start_end_time,
    )

    after_hour_blocks.set_template("{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}")

    walkin = MultiQNA(
        1, 1,
        True,
        'walkin',
        "Aside from same-day appointments, are you mainly a walk-in clinic?"
    )

    walkin.set_template("{please_choose}")

    next_available_appointments = MultiQNA(
        1, float("inf"),
        getattr(walkin.row, "please_choose", None) == "No",
        'next_available_appointment',
        "Aside from same-day appointments, what are your other appointment types and how long until their next available appointments?",
    )

    next_available_appointments.set_template("{appointment_type} available within {available_within} {unit}")

    return dict(documents={
        ("PCMH_1A_4.doc", URL("init", "policy", "PCMH_1A_4.doc"))
    })

def pcmh_1_a_5():
    """Monitoring no-shows"""
    no_shows_training = MultiQNA(
        1, 1, True,
        'no_shows_training',
        "Does the practice actively monitor no-shows with the EMR?"
    )

    no_shows_training.add_warning(
        getattr(no_shows_training.row, "please_choose", None) == "No",
        ("The practice must begin monitoring patient no-shows <b>as soon as possible</b>. No-shows are calculated by "
         "measuring the ratio of patients who arrived for their appointment (numerator) to the total number of patients"
         " scheduled for any appointment for a given time period. NCQA requires a no-show report spanning for at "
         "least 30 days. Please see <a href=''>this guide</a> to see how to do this with your EMR.").format(url=None)
    )

    no_shows_training.set_template("{please_choose}")
    return dict(documents={})

def pcmh_2_b_3_4():
    """Transition of Care"""

    transition_of_care_plan_internal = MultiQNA(
        1, 1, True,
        'transition_of_care_plan_internal',
        "Does the practice have a transition of care plan for importing a patient from pediatric care?"
    )

    transition_of_care_plan_internal.add_warning(
        getattr(transition_of_care_plan_internal.row, "please_choose", None) == "No",
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
        getattr(intake_form.row, "please_choose", None) == "No",
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

    intake_form_patient_example.set_template("<b class='text-success'>{patient_first_name} {patient_last_name}, "
                                             "{patient_DOB} {note}</b>")

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

def pcmh_3_b_4b_4c():
    """Record Review Workbook"""
    return dict(documents={})

# (2)###################################################


# (3)###################################################


# (4)###################################################


# (5)###################################################


# (6)###################################################


# (end)###################################################

request.nav = Navigator()


def index():
    pcmh = int(request.args(0) or 0)
    url = request.nav[pcmh]['index']
    redirect(url)

response.view = 'templates/survey_extend.html'  # http://stackoverflow.com/questions/8750723/is-it-possible-to-change-a-web2py-view-on-the-fly


def a():
    same_day_appointments = SingleQNA(
        True,
        'same_day_appointments',
        "Does the practice reserve time every clinical day for same-day appointments?"
    )

    same_day_appointments.add_warning(
        getattr(same_day_appointments.row, "please_choose", None) == "N",
        T(("{practice_name} <b>MUST</b> reserve time every day that patients are seen for same-day appointments. It "
           "is a requirement for PCMH certification at any level. We recommend at least two 15 minute slots reserved "
           "visibly in your scheduler, for <u>each day patients are seen</u>. Please see <a href='{url}'>these "
           "examples</a> of ideal same-day scheduling.").format(practice_name=_practice.practice_name, url=None))
    )

    same_day_blocks = MultiQNA(
        3, False,  # change the 3 to the number of days the practice is open from the info
        getattr(same_day_appointments.row, "please_choose", None) == "Y",
        'same_day_block',
        "Enter your same-day time blocks. You must have same-day blocks for each day your practice sees patients.",
        validator=_validate_start_end_time,
    )

    #same_day_block.add_formatted_time_fields()
    same_day_blocks.set_template("<b class='text-success'>{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}</b> <i>{note}</i>")


    after_hours = SingleQNA(
        True,
        'after_hours',
        "Does the practice have any after hours, <u>at least</u> once a week?"
    )

    after_hour_blocks = MultiQNA(
        1, False,
        getattr(after_hours.row, "please_choose", None) == "Y",
        'after_hour_block',
        "You said you have after-hours. Please enter your after-hours here.",
        validator=_validate_start_end_time,
    )

    after_hour_blocks.set_template("<b class='text-success'>{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}</b> <i>{note}</i>")

    walkin = SingleQNA(
        True,
        'walkin',
        "Aside from same-day appointments, are you mainly a walk-in clinic?"
    )

    next_available_appointments = MultiQNA(
        1, False,
        getattr(walkin.row, "please_choose", None) == "N",
        'next_available_appointment',
        "Aside from same-day appointments, what are your other appointment types and how long until their next available appointments?",
    )

    next_available_appointments.set_template("<b class='text-success'>{appointment_type} available within {available_within} {unit}</b> <i>{note}</i>")

    return dict(documents={
        ("PCMH_1A_4.doc", URL("init", "policy", "PCMH_1A_4.doc"))
    })


def b():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    # response.flash = T("Hello World")

    transition_of_care_plan_internal = SingleQNA(
        True,
        'transition_of_care_plan_internal',
        "Does the practice have a transition of care plan for importing a patient from pediatric care?"
    )

    transition_of_care_plan_internal.add_warning(
        getattr(transition_of_care_plan_internal.row, "please_choose", None) == "N",
        XML(T("Please schedule a training session with your trainer. Change your answer after training."))
    )

    intake_form = SingleQNA(
        getattr(transition_of_care_plan_internal.row, "please_choose", None) == "Y",
        'intake_form',
        "Do you have an intake form for transitioning a pediatric patient into your practice?"
    )

    intake_form.add_warning(
        getattr(intake_form.row, "please_choose", None) == "N",
        XML(T("Please download this {intake_form_url} and customize it. Change your answer when you're done".format(
            intake_form_url=A("template", _href=URL("policy", "ADHD_screening_letter.doc"))
        )))
    )

    intake_form_upload = MultiQNA(
        1, False,
        getattr(intake_form.row, "please_choose", None) == "Y",
        'intake_form_upload',
        "You said you have an intake form. Please upload a copy of this intake form here.",
        validator=_validate_filename,
    )

    intake_form_upload.set_template("<b><a href='%s'>{filename}</a></b>" % URL('download', args="{upload}",
                                                                               url_encode=False))  # encode escapes {}

    intake_form_patient_example = MultiQNA(
        3, False,
        getattr(intake_form.row, "please_choose", None) == "Y",
        'intake_form_patient_example',
        "Enter <u>3 or more</u> patient names where each patient has a completed intake form in the patient record.",
    )

    intake_form_patient_example.set_template("<b class='text-success'>{patient_first_name} {patient_last_name}, {patient_DOB} {note}</b>")

    return dict(documents={})


def index():
    return a()

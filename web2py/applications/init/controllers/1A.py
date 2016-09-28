response.view = 'templates/survey_extend.html'  # http://stackoverflow.com/questions/8750723/is-it-possible-to-change-a-web2py-view-on-the-fly

def index():

    same_day_appointments = SingleQNA(
        True,
        'same_day_appointments',
        "Does the practice reserve time every clinical day for same-day appointments?"
    )

    same_day_appointments.add_warning(
        getattr(same_day_appointments.row, "please_choose", None) == "N",
        T(("{PRACTICE_NAME} <b>MUST</b> reserve time every day that patients are seen for same-day appointments. It "
           "is a requirement for PCMH certification at any level. We recommend at least two 15 minute slots reserved "
           "visibly in your scheduler, for <u>each day patients are seen</u>. Please see <a href='%s'>these "
           "examples</a> of ideal same-day scheduling.") % None)
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

    return dict(documents = {
        ("PCMH_1A_4.doc", URL("init", "policy", "PCMH_1A_4.doc"))
    })

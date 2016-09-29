response.view = 'templates/survey_extend.html'  # http://stackoverflow.com/questions/8750723/is-it-possible-to-change-a-web2py-view-on-the-fly

def index():
    practice_info = SingleQNA(
        True,
        'practice_info',
        "Enter the information about your practice here."
    )

    clincial_hours = MultiQNA(
        3, False,
        True,
        'clinical_hour',
        "What are the practice's office hours? Only include hours when patients are <u>actually seen</u>.",
        validator=_validate_start_end_time,
    )

    primary_contact = SingleQNA(
        True,
        'primary_contact',
        "Enter the primary contact who is able to handle all inquiries regarding this PCMH project."
    )

    clincial_hours.set_template("<b class='text-success'>{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}</b> <i>{note}</i>")


    return dict(documents={})

def staff():
    providers = MultiQNA(
        1, False,  # change the 3 to the number of days the practice is open from the info
        True,
        'provider',
        "Enter your providers here.",
    )

    days = providers
    providers.set_template("<b class='text-success'>{first_name} {last_name}, {role} <i class='weak-font'>{note}</i><br>&emsp;Usually in office on: {days_of_the_week}</b>")


    has_non_provider = SingleQNA(
        True,
        'has_non_provider',
        "Aside from yourself and other providers, do you have any other staff (i.e. MA's, front desk, office manager, etc.)?"
    )

    non_providers = MultiQNA(
        1, False,  # change the 3 to the number of days the practice is open from the info
        getattr(has_non_provider.row, "please_choose", None) == "Y",
        'non_provider',
        "You said you have non-provider staff. Enter your non-provider staff here.",
    )

    non_providers.set_template("<b class='text-success'>{first_name} {last_name}, {role} <i class='weak-font'>{note}</i><br>&emsp;Usually in office on: {days_of_the_week}</b>")

    return dict(documents={})
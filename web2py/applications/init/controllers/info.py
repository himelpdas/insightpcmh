response.view = 'templates/survey_extend.html'  # http://stackoverflow.com/questions/8750723/is-it-possible-to-change-a-web2py-view-on-the-fly


def index():
    practice_info = MultiQNA(
        1,1,
        True,
        'practice_info',
        "Enter the information about your practice here."
    )

    practice_info.set_template("Practice: {practice_name} ({practice_specialty})<br>Phone: {phone} {extension}"
                               "<br>Address 1: {address_line_1}<br>Address 2: {address_line_2}<br>City: {city}<br>"
                               "State: {state_}<br>Web: {website}")

    clincial_hours = MultiQNA(
        3, float("inf"),
        True,
        'clinical_hour',
        "What are the practice's office hours? Only include days when patients are <u>actually seen</u>.",
        validator=_validate_start_end_time,
    )

    clincial_hours.set_template("{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}")

    primary_contact = MultiQNA(
        1, 1,
        practice_info.row,
        'primary_contact',
        "Enter the primary contact who is able to handle all inquiries regarding this PCMH project."
    )

    primary_contact.set_template("{first_name} {last_name} ({role})<br>{email}<br>{phone} {extension}")

    return dict(documents={})


def staff():
    providers = MultiQNA(
        1, float("inf"),  # change the 3 to the number of days the practice is open from the info
        True,
        'provider',
        "Enter your providers here.",
    )

    days = providers
    providers.set_template(
        "<b class='text-success'>{first_name} {last_name}, {role}<br>&emsp;Usually in office on: {days_of_the_week}</b>")

    has_non_provider = MultiQNA(
        1, 1,
        True,
        'has_non_provider',
        "Aside from yourself and other providers, do you have any other staff (i.e. MA's, front desk, office manager, etc.)?"
    )

    has_non_provider.set_template(
        "{please_choose}")


    non_providers = MultiQNA(
        1, float("inf"),  # change the 3 to the number of days the practice is open from the info
        getattr(has_non_provider.row, "please_choose", None) == "Yes",
        'non_provider',
        "You said you have non-provider staff. Enter your non-provider staff here.",
    )

    non_providers.set_template(
        "{first_name} {last_name}, {role}&emsp;Usually in office on: {days_of_the_week}")

    return dict(documents={})


def emr():
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
        1, 1,  # change the 3 to the number of days the practice is open from the info
        getattr(account_created.row, "please_choose", None) == "Yes",
        'emr_credentials',
        "Please provide the username and password to the account.",
    )

    emr_credentials.set_template(
        "{gpg_encrypted}")

    return dict(documents={})

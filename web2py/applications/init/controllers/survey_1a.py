response.view = 'templates/survey_extend.html'  # http://stackoverflow.com/questions/8750723/is-it-possible-to-change-a-web2py-view-on-the-fly

def same_day_appointments():
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

    same_day_block = MultiQNA(
        20, False,
        getattr(same_day_appointments.row, "please_choose", None) == "Y",
        'same_day_block',
        "Enter your same-day time blocks. You must have same-day blocks for each day your practice sees patients.",
        validator=_validate_start_end_time,
    )

    #same_day_block.add_formatted_time_fields()
    same_day_block.set_template("<b class='text-success'>{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}</b> <i>{note}</i>")

    return dict()

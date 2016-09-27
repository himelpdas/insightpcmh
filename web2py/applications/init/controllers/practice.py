response.view = 'templates/survey_extend.html'  # http://stackoverflow.com/questions/8750723/is-it-possible-to-change-a-web2py-view-on-the-fly

def clinical_hours():
    clinical_hours = MultiQNA(
        3, False,
        True,
        'clinical_hours',
        "Enter your regular office days and hours. These are the days and hours where you see patients.",
        validator=_validate_start_end_time
    )

    clinical_hours.set_template("<b class='text-success'>{day_of_the_week} {start_time:%I}:{start_time:%M} "
                                "{start_time:%p} - {end_time:%I}:{end_time:%M} {end_time:%p}</b> <i>{note}</i>")

    return dict()
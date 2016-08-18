# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    #response.flash = T("Hello World")

    transition_of_care_plan_internal = question_and_answer(
        True,
        db.transition_of_care_plan_internal,
        "Does the practice have a transition of care plan for importing a patient from pediatric care?"
    )
    transition_of_care_plan_internal.addWarnings(
        getattr(transition_of_care_plan_internal.row, "please_choose", None) == "N",
        XML(T("Please schedule a training session with your trainer. Change your answer after training."))
    )

    intake_form = question_and_answer(
        getattr(transition_of_care_plan_internal.row, "please_choose", None) == "Y",
        db.intake_form,
        "Do you have an intake form for transitioning a pediatric patient into your practice?"
    )
    intake_form.addWarnings(
        getattr(intake_form.row, "please_choose", None) == "N",
        XML(T("Please download this {intake_form_url} and customize it. Change your answer when you're done".format(
            intake_form_url=A("template", _href=URL("policy", "ADHD_screening_letter.doc"))
        )))
    )

    intake_form_upload = question_and_answer(
        getattr(intake_form.row, "please_choose", None) == "Y",
        db.intake_form_upload,
        "You said you have an intake form. Please upload a copy of this intake form here.",
        validator=VALIDATE_FILENAME
    )

    intake_form_patient_example = question_and_answer(
        getattr(intake_form.row, "please_choose", None) == "Y",
        db.intake_form_patient_example,
        XML("Enter <u>3 or more</u> patient names where each patient has a completed intake form in the patient record."),
        multi=3
    )

    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

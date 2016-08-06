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

    transition_of_care_plan_internal_row, transition_of_care_plan_internal_form = \
        FORM_PROCESSOR_GENERIC(True, db.transition_of_care_plan_internal)

    intake_form_row, intake_form_form = FORM_PROCESSOR_GENERIC(getattr(
        transition_of_care_plan_internal_row, "please_choose", None) == "Y",
                                                               db.intake_form)

    intake_form_upload_row = None
    intake_form_upload_form = None
    if intake_form_row and intake_form_row.please_choose == "Y":
        intake_form_upload_row = db(db.intake_form_upload.id > 0).select().last()
        intake_form_upload_form = SQLFORM_ANSWER(db.intake_form_upload, intake_form_upload_row)
        if intake_form_upload_form.process(onvalidation=VALIDATE_FILENAME).accepted:
            session.flash = "Answer saved!"
            redirect(URL())

    intake_form_patient_example_row = None
    intake_form_patient_example_form = None
    if getattr(intake_form_row, "please_choose", None) == "Y":
        intake_form_patient_example_row = db(db.intake_form_patient_example.id > 0).select().last()
        intake_form_patient_example_form = SQLFORM_ANSWER(db.intake_form_patient_example,
                                                          intake_form_patient_example_row)
        if intake_form_patient_example_form.process().accepted:
            session.flash = "Answer saved!"
            redirect(URL())

    return dict(transition_of_care_plan_internal_form=transition_of_care_plan_internal_form,
                transition_of_care_plan_internal_row=transition_of_care_plan_internal_row,
                intake_form_form=intake_form_form,
                intake_form_row=intake_form_row,
                intake_form_upload_form=intake_form_upload_form,
                intake_form_upload_row=intake_form_upload_row,
                intake_form_patient_example_form=intake_form_patient_example_form,
                intake_form_patient_example_row=intake_form_patient_example_row)

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

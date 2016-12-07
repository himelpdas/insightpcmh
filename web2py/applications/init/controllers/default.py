# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
from collections import OrderedDict

def _disable_rbac_fields(func):
    def inner():  # http://stackoverflow.com/questions/19673284/how-do-i-get-list-of-field-objects-in-a-table-in-web2py
        for rbac in [db.auth_membership, db.auth_permission, db.auth_group]:
            for field in rbac:
                field.readable = False
                field.writable = False
        return func
    return inner()


@_disable_rbac_fields
@auth.requires_login()
def index():
    # web2py performs inner joins automatically and transparently when the query links two or more tables

    return dict()


@_disable_rbac_fields
@auth.requires_signature()
def load_apps_grid():
    links = [dict(header='',  # header is col title
                  body=lambda row:
                  A(SPAN(_class="glyphicon glyphicon-play-circle"),
                    _class="btn btn-sm btn-success",
                    _href=URL('init', "0", 'index.html',  # table may or may not be joined
                              vars=dict(app_id=getattr(row, "application", row).id))))]

    if auth.has_membership("admins"):
        links.append(dict(
            header=SPAN("Assigned", _class="text-success"),
            body=lambda e: ""
        ))

        my_apps = db((db.application.id > 0))
        onvalidation = None
        db.application.owner_id.readable = True
        db.application.owner_id.writable = True

        trainers = db((db.auth_group.id == db.auth_membership.group_id) &
                      (db.auth_group.role == "trainers") &
                      (db.auth_user.id == db.auth_membership.user_id)
                      ).select()
        options = OrderedDict()
        for trainer in trainers:
            name = "%s%s%s" % (trainer.auth_user.first_name.capitalize()[0],
                               trainer.auth_user.last_name.capitalize()[0],
                               trainer.auth_user.id)
            options[name] = trainer.auth_user.id

        def _trainer_select(row):
            #return DIV(*[BUTTON(each, _class="btn btn-sm btn-warning", _type="button") for each in options],
            #_class="btn-group", _style="display:flex"  # https://github.com/twbs/bootstrap/issues/9939
            return DIV(SELECT(OPTION("hello", _value="1"),OPTION("hello", _value="2"), _multiple="multiple"),
                       _style="display:flex")


        links.append(dict(
            header=SPAN("Available Trainers", _class="text-warning"),
            body=_trainer_select
        ))

        # app managers
        app_managers = db((db.auth_group.id == db.auth_membership.group_id) &
                          (db.auth_group.role == "app_managers") &
                          (db.auth_user.id == db.auth_membership.user_id)
                          ).select()
        options = OrderedDict()
        for app_manager in app_managers:
            name = "%s%s%s" % (app_manager.auth_user.first_name.capitalize()[0],
                           app_manager.auth_user.last_name.capitalize()[0],
                           app_manager.auth_user.id)
            options[name] = app_manager.auth_user.id

        def _app_manager_select(row):
            return DIV(*[BUTTON(each, _class="btn btn-sm btn-danger", _type="button") for each in options],
                       _class="btn-group", _style="display:flex"  # https://github.com/twbs/bootstrap/issues/9939
                       )

        links.append(dict(
            header=SPAN("Available Managers", _class="text-danger"),
            body=_app_manager_select
        ))

    else:
        my_group_id = auth.id_group("user_%s" % auth.user.id)
        my_apps = db((db.application.id == db.auth_permission.record_id) &
                     (db.auth_permission.name == "manage") &
                     (db.auth_permission.group_id == my_group_id))
        onvalidation = _app_onvalidation

    app_grid = SQLFORM.grid(my_apps,
                            onvalidation=onvalidation,
                            oncreate=_app_oncreate,
                            formname="load_apps_grid",
                            links=links,
                            links_placement='left')

    return dict(app_grid=app_grid)


@_disable_rbac_fields
@auth.requires_signature()
def load_admins_grid():
    admins = db((db.auth_group.id == db.auth_membership.group_id) &
                (db.auth_group.role == "admins") &
                (db.auth_user.id == db.auth_membership.user_id)
                )

    admin_grid = SQLFORM.grid(admins,
                              formname="load_admins_grid")

    return dict(admin_grid=admin_grid)


@_disable_rbac_fields
@auth.requires_signature()
def load_trainers_grid():
    # the index page checks for permissions, then generates this sig, so that we don't have to keep checking permissions
    trainers = db((db.auth_group.id == db.auth_membership.group_id) &
                  (db.auth_group.role == "trainers") &
                  (db.auth_user.id == db.auth_membership.user_id)
                  )

    trainer_grid = SQLFORM.grid(trainers,
                                formname="load_trainers_grid",  # must change formname or else form will save as another
                                links_placement="left")

    return dict(trainer_grid=trainer_grid)


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


#auth.requires(not auth.has_membership(user_id=getattr(auth.user, "id", None), role="trainers") and
#               not auth.has_membership(user_id=getattr(auth.user, "id", None), role="admins")
#               , requires_login=True)
def _app_onvalidation(form):
    form.vars.owner_id = auth.user.id


def _app_oncreate(form):
    app_id = form.vars.id
    auth.add_permission(0, "manage", 'application', app_id)  # 0 means user_1
    auth.add_permission(auth.id_group("admins"), "manage", 'application', app_id)
    # app_url = URL('application', vars=dict(app_id=form.vars.id), hmac_key=MY_KEY)
    #redirect(URL(0, "index.html", vars=dict(app_id=form.vars.id)))  # redir user to his app


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

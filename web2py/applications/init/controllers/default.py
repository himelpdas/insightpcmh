# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

@auth.requires_login()
def index():
    # web2py performs inner joins automatically and transparently when the query links two or more tables
    my_app_memberships = db((db.auth_membership.user_id == auth.user.id) &
                 (db.auth_group.id == db.auth_membership.group_id) &  # inner join
                 (db.auth_group.role.contains("application_"))).select()
    my_apps = []
    for my_membership in my_app_memberships:
        my_membership_app_id = my_membership.auth_group.role.split("_")[-1]
        my_app = db((db.application.id == my_membership_app_id)).select().last()
        members_of_my_app = db((db.auth_membership.group_id == my_membership.auth_membership.group_id) &
                               (db.auth_user.id == db.auth_membership.user_id)).select()
        my_app.members_of_my_app = members_of_my_app
        my_app.my_membership = my_membership
        my_apps.append(my_app)

    return dict(my_apps=my_apps)


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


@auth.requires(not auth.has_membership(user_id=getattr(auth.user, "id", None), role="trainers") and
               not auth.has_membership(user_id=getattr(auth.user, "id", None), role="admins")
               , requires_login=True)
def new_application():
    response.view = "default/application.html"

    def set_application_id(form):
        form.vars.owner_id = auth.user.id

    form = SQLFORM(db.application)
    if form.process(detect_record_change=True, onvalidation=set_application_id).accepted:
        response.flash = "Application information created!"
        app_gid = auth.add_group("application_%s" % form.vars.id, "users allowed to edit application_%s" % form.vars.id)
        auth.add_membership(group_id=app_gid, user_id=auth.user.id)

        URL('index', vars=dict(app_id=form.vars.id), hmac_key=MY_KEY)
        redirect(URL("index"))

    return dict(form=form)


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

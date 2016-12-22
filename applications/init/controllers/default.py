# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
from collections import OrderedDict
import json
import datetime


def _disable_rbac_fields(func):
    """when displaying a grid with something joined, sometimes the auth tables joined are not necessary"""
    def inner():  # http://stackoverflow.com/questions/19673284/how-do-i-get-list-of-field-objects-in-a-table-in-web2py
        for rbac in [db.auth_membership, db.auth_permission, db.auth_group]:
            for field in rbac:
                field.readable = False
                field.writable = False
        db.application.owner_id.readable = True
        return func
    return inner()


def index():
    # web2py performs inner joins automatically and transparently when the query links two or more tables
    response.title = "PCMH Dashboard"
    return dict()


@_disable_rbac_fields
@auth.requires_login()
def dash():
    # web2py performs inner joins automatically and transparently when the query links two or more tables
    response.title = "PCMH Dashboard"
    return dict()

@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT or "",
                          hash_vars=["revoke_participant", "permission", "row_id"]))
def revoke_user():
    e = request.get_vars["revoke_participant"]
    p = request.get_vars["permission"]
    r = request.get_vars["row_id"]
    del request.get_vars["row_id"]
    del request.get_vars["revoke_participant"]
    del request.get_vars["permission"]
    del request.get_vars["_signature"]

    logger.warn("Revoking, user id, permission, row, self-group:\n%s, %s, %s, %s" % (e, p, r, auth.id_group("user_%s" % e)))

    auth.del_permission(auth.id_group("user_%s" % e), p, "application", r)  # 0 means user_1

    session.flash = "Revoked user from application ID%s" % r
    redirect(URL("dash.html", args=request.args, vars=request.get_vars))


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT or "",
                      hash_vars=["assign_participant", "permission", "row_id"]))
def assign_user():

    e = request.get_vars["assign_participant"]
    p = request.get_vars["permission"]
    r = request.get_vars["row_id"]
    del request.get_vars["row_id"]
    del request.get_vars["assign_participant"]
    del request.get_vars["permission"]
    del request.get_vars["_signature"]

    auth.add_permission(auth.id_group("user_%s" % e), p, "application", r)  # 0 means user_1

    session.flash = "Assigned user to application ID%s" % r
    redirect(URL("dash.html", args=request.args, vars=request.get_vars))


def _assigned_column(row):
    row.id = getattr(row, 'id', None) or getattr(row.application, 'id', None)  # can be from join or regular query

    assert row.id, "expected row.id"

    participators = db(
        # JOIN SECTION
        (db.auth_group.id == db.auth_membership.group_id) &  # join auth_group and auth_membership
        (db.auth_user.id == db.auth_membership.user_id) &  # join auth_user and auth_membership
        (db.auth_permission.group_id == db.auth_group.id) &  # join auth_permission and auth_group
        # FILTER SECTION
        (db.auth_permission.record_id == row.id) &  # only where permission is given to this record
        (db.auth_permission.table_name == "application") &
        (db.auth_permission.name.belongs("manage", "train", "contribute"))  # trainers app mgrs and users
    ).select()
    #
    #print participators
    participator_widgets = []
    for participator in participators:
        base = dict(
            c_id=participator.auth_user.id,
            c_fn=participator.auth_user.first_name.capitalize(),
            c_ln=participator.auth_user.last_name.capitalize(),
            c_email=participator.auth_user.email,
        )
        base.update(
            c_posessive="%s's" % base["c_fn"],
            c_name="%s %s (%s)" % (base['c_fn'], base['c_ln'], base['c_id']),
            c_name_html="%s %s <span class='text-muted'>(%s)</span>" % (base['c_fn'], base['c_ln'], base['c_id']),
            c_acronym="%s%s%s" % (participator.auth_user.first_name.capitalize()[0],
                                  participator.auth_user.last_name.capitalize()[0],
                                  participator.auth_user.id),
        )
        if auth.has_membership(user_id=participator.auth_user.id, role="trainers") and \
                        participator.auth_permission.name == "train":
            participator_widgets.append(dict(color="danger", title="trainer", permission="train",
                                            c_title=base['c_name']+" (Trainer)",
                                            c_title_html=base['c_name_html'] +
                                            " <span class='text-danger'>(Trainer)</span>", **base))
        if auth.has_membership(user_id=participator.auth_user.id, role="app_managers") and \
                        participator.auth_permission.name == "manage":
            participator_widgets.append(dict(color="warning", title="app_manager", permission="manage",
                                            c_title=base['c_name']+" (App Manager)",
                                            c_title_html=base['c_name_html'] +
                                            " <span class='text-warning'>(App Manager)</span>", **base))  # it is possible to be two roles
        if auth.has_membership(user_id=participator.auth_user.id, role="contributors") and \
                        participator.auth_permission.name == "contribute":
            participator_widgets.append(dict(color="success", title="contributor", permission="contribute",
                                            c_title=base['c_name']+" (Contributor)",
                                            c_title_html=base['c_name_html'] +
                                            " <span class='text-success'>(Contributor)</span>", **base))

    for participator_widget in participator_widgets:
        revoke_id = "revoke_participant_%s_%s_%s" % (participator_widget["title"], participator_widget["c_id"], row.id)
        widget_script = """
        {select}<script>
            $(document).ready(function(){{
            $("#{revoke_id}").val('').multiselect({{
                nonSelectedText: '{c_acronym}',
                onChange: function(option, checked, select) {{
                    window.location = '{url}';
                }},
                buttonClass: 'btn btn-sm btn-{color}', disableIfEmpty: true, enableHTML: true}});
            }})
        </script>"""
        widget = None
        widget_a = XML("<button class='btn btn-sm btn-{color}' title='{c_email}'>{c_acronym}</button>".format(
                color=participator_widget["color"],
                c_acronym=participator_widget["c_acronym"],
                c_email=participator_widget["c_email"],  # todo change to popover
        ))
        widget_b = XML(widget_script.format(
            c_acronym=participator_widget["c_acronym"],
            revoke_id=revoke_id,
            color=participator_widget["color"],
            url=URL("revoke_user.html",
                    vars=dict(
                        revoke_participant=participator_widget["c_id"],
                        permission=participator_widget["permission"],
                        row_id=row.id,
                        **request.get_vars),
                    hmac_key=MY_KEY, salt=session.MY_SALT or "",
                    hash_vars=["revoke_participant", "permission", "row_id"]
                    ),
            select=SELECT(OPTGROUP(OPTION("Revoke %s access to this application" % participator_widget['c_posessive']),
                                   _label=participator_widget['c_title_html'] + ":"),
                          _id=revoke_id,
                          _class="assigned", )
        ))

        if auth.has_membership("contributor"):
            widget = widget_a
        elif auth.has_membership("admins") or auth.has_membership("masters"):
            widget = widget_b
        elif auth.has_membership("trainers"):
            if participator_widget["title"] == "contributor":
                widget = widget_a
            else:
                widget = widget_b

        #assert(widget, "expected a widget!")

        participator_widget.update(dict(
            widget=widget
        ))

    employees = db((db.auth_group.id == db.auth_membership.group_id) &
                   (db.auth_group.role.belongs("trainers", "app_managers")) &
                   (db.auth_user.id == db.auth_membership.user_id)).select()

    employee_options = []
    assign_urls = {}

    title = e_title = e_title_html = permission = None
    for employee in employees:
        e_id = employee.auth_user.id
        e_fn = employee.auth_user.first_name.capitalize()
        e_ln = employee.auth_user.last_name.capitalize()
        e_email = employee.auth_user.email
        e_name = "%s %s (%s)" % (e_fn, e_ln, e_id)
        e_name_html = "%s %s <span class='text-muted'>(%s)</span>" % (e_fn, e_ln, e_id)

        if employee.auth_group.role == "trainers":
            title = "trainer"
            permission = "train"
            e_title = e_name + " (trainer)"
            e_title_html = e_name_html + " <span class='text-danger'>(Trainer)</span>"        
        
        if employee.auth_group.role == "app_managers":
            title = "app_manager"
            permission = "manage"
            e_title = e_name + " (App Mananger)"
            e_title_html = e_name_html + " <span class='text-warning'>(App Manager)</span>"

        assign_id = "%s_%s" % (title, e_id)
        assign_urls[assign_id] = URL("assign_user.html",
                                     vars=dict(
                                         assign_participant=e_id,
                                         permission=permission,
                                         row_id=row.id,
                                         **request.get_vars),
                                     hmac_key=MY_KEY, salt=session.MY_SALT or "",
                                     hash_vars=["assign_participant", "permission", "row_id"]
                                     )
        # if not already in revoke buttons
        if not "%s_%s" % (title, e_id) in map(lambda w: "%s_%s" % (w["title"], w["c_id"]), participator_widgets):
            employee_options.append(OPTION(e_title_html, _value=assign_id))

    employees_and_participants = set(map(lambda e: e.auth_user.id, employees) + map(lambda e: e.auth_user.id, 
                                                                                    participators))
    # a_week_ago = request.now - datetime.timedelta(days=7)
    recent = db(db.auth_user.created_on > 0).select(orderby=~db.auth_user.modified_on, limitby=(0, 5))
    recent.exclude(lambda r: r.id in employees_and_participants or r.is_insight)
    recent_options = []
    
    for new in recent:
        n_id = new.id
        n_fn = new.first_name.capitalize()
        n_ln = new.last_name.capitalize()
        n_email = new.email
        n_name = "%s %s (%s)" % (n_fn, n_ln, n_id)
        n_name_html = "%s %s <span class='text-muted'>(%s) (%s)</span>" % (n_fn, n_ln, n_id, n_email)
        assign_id = "new_%s" % n_id
        assign_urls[assign_id] = URL("assign_user.html",
                                     vars=dict(
                                         assign_participant=n_id,
                                         permission="contribute",
                                         row_id=row.id,
                                         **request.get_vars),
                                     hmac_key=MY_KEY, salt=session.MY_SALT or "",
                                     hash_vars=["assign_participant", "permission", "row_id"]
                                     )
        recent_options.append(OPTION(n_name_html, _value=assign_id))

    employee_optgroup = OPTGROUP(*employee_options, _label="Assign an employee:")
    recent_optgroup = OPTGROUP(*recent_options, _label="Assign a recent contributor:")

    assign_optgroups = []
    enable_participant_assign_select = True
    if IS_ADMIN or IS_MASTER:
        if recent_options:
            assign_optgroups.append(recent_optgroup)
        if employee_options:
            assign_optgroups.append(employee_optgroup)
    elif IS_TRAINER or IS_MANAGER:  # let trainers assign a recent user
        assign_optgroups.append(recent_optgroup)
    else:
        enable_participant_assign_select = False

    all_widgets = map(lambda e: e['widget'], participator_widgets)

    if enable_participant_assign_select:
        all_widgets.append(XML("""{select}<script>
                    $(document).ready(function(){{
                    urls_{row_id} = {urls};
                    $("#assign_participant_{row_id}").val('').multiselect({{
                        nonSelectedText: '<span class="glyphicon glyphicon-plus"></span>',
                        onChange: function(option, checked, select) {{
                            window.location = urls_{row_id}[$(option).val()];
                        }},
                        buttonClass: 'btn btn-sm', disableIfEmpty: true, enableHTML: true}});
                    }})
                </script>""".format(  #http://bit.ly/2g9PyCl select remove default choice, then style with multiselect
            select=SELECT(
                *reversed(assign_optgroups),
                _id="assign_participant_%s" % row.id,
                _class="assign_participants"
            ),
            row_id=row.id,
            urls=json.dumps(assign_urls)
        )))  # , _multiple="multiple")  # only one choice

    container = DIV(*all_widgets, _style="display:flex")
    return container


#@_disable_rbac_fields
# @auth.requires_signature()
def load_apps_grid():
    # db.application.modified_by.readable = True
    # db.application.created_by.readable = True
    # db.application.created_on.readable = True
    # db.application.modified_on.readable = True

    links = [dict(header='',  # header is col title
                  body=lambda row:
                  A(SPAN(_class="glyphicon glyphicon-play"),
                    _class="btn btn-sm btn-default",
                    _title="Start",
                    _href=URL('init', "0", 'index.html',  # table may or may not be joined
                              vars=dict(app_id=getattr(row, "application", row).id))))]

    onvalidation = None
    if not IS_TEAM:  # add contributor
        onvalidation = _app_onvalidation  # indicates new app owner
    if IS_MASTER or IS_ADMIN:
        db.application.owner_id.writable = True
    if IS_MASTER:  # remove not after testing non-master mode
        my_apps_grid = db(db.application.id > 0)
    else:
        my_group_id = auth.id_group("user_%s" % auth.user.id)
        my_apps_disinct = db((db.application.id == db.auth_permission.record_id) &  # same application id will show up
                             # twice because multiple permissions of same user can be set for the same application (i.e.
                             # when you see HD1 XXX HD1 in master mode *WARNING*
                     (db.auth_permission.name.belongs(["manage", "contribute", "administrate", "train"])) &
                     (db.auth_permission.group_id == my_group_id)).select(distinct=db.application.id)  # or you can use
        # groupby http://bit.ly/2h0Ou3Z

        logger.info(my_apps_disinct)

        my_apps_grid = db.application.id.belongs(map(lambda r: r.application.id, my_apps_disinct))  # will have to
        # double query because grid does not have distinct and groupby disables CUD

    links.append(dict(
        header="Participants",  # can use SPAN
        body=_assigned_column
    ))

    app_grid = SQLFORM.grid(my_apps_grid,
                            onvalidation=onvalidation,
                            oncreate=_app_oncreate,
                            formname="load_apps_grid",
                            links=links,
                            # groupby=db.application.id,  # groupby by itself behaves like distinct http://bit.ly/2h0Ou3Z
                            field_id=db.application.id,
                            links_placement='left')

    return dict(app_grid=app_grid)


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT or "", hash_vars=["group", "action",
                                                                                           "user_id"]))
def add_remove_user():
    u = request.get_vars["user_id"]
    a = request.get_vars["action"]
    g = request.get_vars["group"]
    del request.get_vars["group"]
    del request.get_vars["action"]
    del request.get_vars["user_id"]
    del request.get_vars["_signature"]

    user = db(db.auth_user.id == u).select().last()

    assert(user, "expected user!")

    if a == "+":
        auth.add_membership(role=g, user_id=u)
        word = "added"
        direction = "to"
    else:
        auth.del_membership(role=g, user_id=u)
        word = "removed"
        direction = "from"
    session.flash = '%s was %s %s the group "%s"' % (user.first_name.capitalize(), word, direction, g.replace("_"," "))
    redirect(URL("dash.html", args=request.args, vars=request.get_vars))


def _employee_group_links(row):
    _p = SPAN(_class="glyphicon glyphicon-plus")  # plus or minus
    _m = SPAN(_class="glyphicon glyphicon-minus")

    if row.is_insight:
        groups = [("admins", "info"), ("app_managers", "warning"), ("trainers", "danger")]
    else:
        groups = [("contributors", "success")]
    all_links = []
    for each in groups:
        group = each[0]
        group_name = group.capitalize().replace("_", " ")
        color = each[1]
        action = "-" if auth.has_membership(role=group, user_id=row.id) else "+"
        sign = _m if action == "-" else _p
        label = XML("%s %s" % (sign, group_name[:-1]))  # take out the s at the end
        all_links.append(A(label, _class="btn btn-sm %s" % (("btn-%s" % color) if action != "+" else "btn-default"),
                           _href=URL("add_remove_user.html",
                                     vars=dict(
                                         user_id=row.id,
                                         group=group,
                                         action=action,
                                         **request.get_vars),
                                     hmac_key=MY_KEY, salt=session.MY_SALT or "",
                                     hash_vars=["user_id", "group", "action"]
                                     ),
                           _title=(("Remove %s from " if action == "-" else "Add %s to ")
                                   % row.first_name.capitalize()) + group_name
                           )
                         )
    return DIV(*all_links, _style="display:flex")


@_disable_rbac_fields
# @auth.requires_signature()
def load_users_grid():
    links = []

    links.append(dict(
        header="Set roles",  # can use SPAN
        body=_employee_group_links
    ))

    users_grid = SQLFORM.grid(db.auth_user,
                              formname="load_users_grid",
                              links=links,
                              onupdate=_user_onupdate,
                              oncreate=_user_oncreate,
                              orderby=~db.auth_user.is_insight | db.auth_user.id,  # show insight first
                              field_id=db.auth_user.id,
                              #user_signature=False,  # this is handled by the controller
                              links_placement='left')

    return dict(users_grid=users_grid)


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


def _user_onupdate(form):  # todo revoke all permissions
    id = form.vars.id
    self_group = auth.id_group("user_%s" % id)
    # auth.del_permission(auth.id_group("user_%s" % e), p, "application", r)  # 0 means user_1
    if not form.vars.is_insight:
        groups = [("admins", "administrate"), ("app_managers", "manage"), ("trainers", "train"), ("masters", None)]
        for group in groups:
            role = group[0]
            permission = group[1]
            auth.del_membership(role=role, user_id=id)
            if permission:
                db((db.auth_permission.group_id == self_group &
                    (db.auth_permission.name == permission))
                   ).delete()
    else:
        auth.del_membership(role="contributors", user_id=id)
        db((db.auth_permission.group_id == self_group &
            (db.auth_permission.name == "contribute"))
           ).delete()


def _user_oncreate(form):
    id = form.vars.id
    self_group = "user_%s" % id
    auth.add_group(self_group, description="Group for user %s. Created in admin panel" % self_group)
    auth.add_membership(role=self_group, user_id=id)


def _app_oncreate(form):
    app_id = form.vars.id
    auth.add_permission(0, "contribute", 'application', app_id)  # 0 means user_1

    if not auth.has_membership("admins"):
        auth.add_membership(role="contributor", user_id=auth.user_id)

    admins = db((db.auth_group.id == db.auth_membership.group_id) &
                (db.auth_group.role == "admins") &
                (db.auth_user.id == db.auth_membership.user_id)
                ).select()

    for admin in admins:
        auth.add_permission(auth.id_group("user_%s" % admin.auth_user.id), "contribute", 'application', app_id)  # 0 means user_1
    #auth.add_permission(auth.id_group("masters"), "administrate", 'application', app_id)
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

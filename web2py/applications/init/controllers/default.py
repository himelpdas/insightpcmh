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

def _disable_rbac_fields(func):
    def inner():  # http://stackoverflow.com/questions/19673284/how-do-i-get-list-of-field-objects-in-a-table-in-web2py
        for rbac in [db.auth_membership, db.auth_permission, db.auth_group]:
            for field in rbac:
                field.readable = False
                field.writable = False
        db.application.owner_id.readable = True
        return func
    return inner()


@_disable_rbac_fields
@auth.requires_login()
def index():
    # web2py performs inner joins automatically and transparently when the query links two or more tables
    response.title = "PCMH Dashboard"
    return dict()


def assign_user():
    if not URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT or "", hash_vars=["assign_employee", "assign_as"]):
        raise HTTP(403)
    else:
        del request.get_vars["assign_employee"]
        del request.get_vars["assign_as"]



    redirect(URL("index.html", *request.args, **request.get_vars))

def _assigned_column(row):
    contributors = db(
        # JOIN SECTION
        (db.auth_group.id == db.auth_membership.group_id) &  # join auth_group and auth_membership
        (db.auth_user.id == db.auth_membership.user_id) &  # join auth_user and auth_membership
        (db.auth_permission.group_id == db.auth_group.id) &  # join auth_permission and auth_group
        # FILTER SECTION
        (db.auth_permission.record_id == row.id) &  # only where permission is given to this record
        (db.auth_permission.name == "manage")  # trainers app mgrs and users
    ).select()
    #
    contributor_widgets = []
    for contributor in contributors:
        base = dict(
            c_id=contributor.auth_user.id,
            c_fn=contributor.auth_user.first_name.capitalize(),
            c_ln=contributor.auth_user.last_name.capitalize(),
            c_email=contributor.auth_user.email,
        )
        base.update(
            c_posessive="%s's" % base["c_fn"],
            c_name="%s %s (%s)" % (base['c_fn'], base['c_ln'], base['c_id']),
            c_name_html="%s %s <span class='text-muted'>(%s)</span>" % (base['c_fn'], base['c_ln'], base['c_id']),
            c_acronym="%s%s%s" % (contributor.auth_user.first_name.capitalize()[0],
                                  contributor.auth_user.last_name.capitalize()[0],
                                  contributor.auth_user.id),
        )
        if auth.has_membership(user_id=contributor.auth_user.id, role="trainers"):
            contributor_widgets.append(dict(color="danger", title="trainer",
                                            c_title=base['c_name']+" (Trainer)",
                                            c_title_html=base['c_name_html'] +
                                            " <span class='text-danger'>(Trainer)</span>", **base))
        if auth.has_membership(user_id=contributor.auth_user.id, role="app_managers"):
            contributor_widgets.append(dict(color="warning", title="app_manager",
                                            c_title=base['c_name']+" (App Manager)",
                                            c_title_html=base['c_name_html'] +
                                            " <span class='text-warning'>(App Manager)</span>", **base))  # it is possible to be two roles
        if not contributor_widgets:  # if neither trainer or app manager
            contributor_widgets.append(dict(color="success", title="contributor",
                                            c_title=base['c_name']+" (Contributor)",
                                            c_title_html=base['c_name_html'] +
                                            " <span class='text-success'>(Contributor)</span>", **base))

    for contributor_widget in contributor_widgets:
        widget_id = "assigned_%s_%s" % (contributor_widget["title"], contributor_widget["c_id"])
        widget_script = """{select}<script>$('#{widget_id}').val('').multiselect({{nonSelectedText: '{c_acronym}',
            buttonClass: 'btn btn-sm btn-{color}', enableHTML: true}});</script>"""

        contributor_widget.update(dict(
            widget=XML(widget_script.format(
                c_acronym=contributor_widget["c_acronym"],
                widget_id=widget_id,
                color=contributor_widget["color"],
                select=SELECT(OPTGROUP(OPTION("Revoke %s access to this application" % contributor_widget['c_posessive']),
                                       _label=contributor_widget['c_title_html']+":"),
                              _id=widget_id)
            ))
        ))

    employees_widgets = filter(lambda e: e['title'] in ["trainer", "app_manager"], contributor_widgets)
    employee_options = []
    assign_urls = {}
    for employees_widget in employees_widgets:
        assign_id = "%s_%s" % (employees_widget["title"], employees_widget["c_id"])
        assign_urls[assign_id] = URL("assign_user.html", vars=dict(assign_employee=employees_widget["c_id"],
                                               assign_as=employees_widget["title"],
                                               **request.get_vars),
                                     hmac_key=MY_KEY, salt=session.MY_SALT or "",
                                     hash_vars=["delete", "app_id"]
                                     )
        employee_options.append(OPTION(employees_widget["c_title_html"], _value=assign_id))

    employee_assign = XML(
        """{select}<script>
                $(document).ready(function(){{
                urls = {urls};
                $("#assign_employee_{row_id}").val('').multiselect({{
                    nonSelectedText: '<span class="glyphicon glyphicon-plus"></span>',
                    onChange: function(option, checked, select) {{
                        window.location = urls[$(option).val()];
                    }},
                    buttonClass: 'btn btn-sm',disableIfEmpty: true,enableHTML: true}});
                }})
            </script>""".format(  #http://bit.ly/2g9PyCl select remove default choice, then style with multiselect
            select=SELECT(
                OPTGROUP(*employee_options, _label="Add user to manage app:"),
                _id="assign_employee_%s" % row.id,
                _class="assign_employees",
            ),
            row_id=row.id,
            urls=json.dumps(assign_urls)
        )
    )  # , _multiple="multiple")  # only one choice
    container = DIV(*map(lambda e: e['widget'], contributor_widgets)+[employee_assign], _style="display:flex")
    return container


@_disable_rbac_fields
@auth.requires_signature()
def load_apps_grid():
    links = [dict(header='',  # header is col title
                  body=lambda row:
                  A(SPAN(_class="glyphicon glyphicon-play"),
                    _class="btn btn-sm btn-default",
                    _href=URL('init', "0", 'index.html',  # table may or may not be joined
                              vars=dict(app_id=getattr(row, "application", row).id))))]

    if auth.has_membership("admins"):

        my_apps = db((db.application.id > 0))
        onvalidation = None
        db.application.owner_id.writable = True

        # trainers = db((db.auth_group.id == db.auth_membership.group_id) &
        #               (db.auth_group.role == "trainers") &
        #               (db.auth_user.id == db.auth_membership.user_id)
        #               ).select()
        # options = OrderedDict()
        # for trainer in trainers:
        #     name = "%s%s%s" % (trainer.auth_user.first_name.capitalize()[0],
        #                        trainer.auth_user.last_name.capitalize()[0],
        #                        trainer.auth_user.id)
        #     options[name] = trainer.auth_user.id
        #
        # def _trainer_select(row):
        #     #return DIV(*[BUTTON(each, _class="btn btn-sm btn-warning", _type="button") for each in options],
        #     #_class="btn-group", _style="display:flex"  # https://github.com/twbs/bootstrap/issues/9939
        #     return DIV(SELECT(OPTION("hello", _value="1"),OPTION("hello", _value="2"), _multiple="multiple"),
        #                _style="display:flex")
        #
        # links.append(dict(
        #     header=SPAN("Trainer(s)", _class="text-warning"),
        #     body=_trainer_select
        # ))
        #
        # # app managers
        # app_managers = db((db.auth_group.id == db.auth_membership.group_id) &
        #                   (db.auth_group.role == "app_managers") &
        #                   (db.auth_user.id == db.auth_membership.user_id)
        #                   ).select()
        # options = OrderedDict()
        # for app_manager in app_managers:
        #     name = "%s%s%s" % (app_manager.auth_user.first_name.capitalize()[0],
        #                    app_manager.auth_user.last_name.capitalize()[0],
        #                    app_manager.auth_user.id)
        #     options[name] = app_manager.auth_user.id
        #
        # def _app_manager_select(row):
        #     return DIV(*[BUTTON(each, _class="btn btn-sm btn-danger", _type="button") for each in options],
        #                _class="btn-group", _style="display:flex"  # https://github.com/twbs/bootstrap/issues/9939
        #                )
        #
        # links.append(dict(
        #     header=SPAN("Available Managers", _class="text-danger"),
        #     body=_app_manager_select
        # ))

    else:
        my_group_id = auth.id_group("user_%s" % auth.user.id)
        my_apps = db((db.application.id == db.auth_permission.record_id) &
                     (db.auth_permission.name == "manage") &
                     (db.auth_permission.group_id == my_group_id))
        onvalidation = _app_onvalidation

    links.append(dict(
        header="Assigned",  # can use SPAN
        body=_assigned_column
    ))

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

# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

MY_KEY = "Himel123"
TALK_TO_API_KEY = "e3730573ebe8f86994e9a07e49f1b0fe5a0fe2af"
MASTER_EMAILS = ["himel@insightmanagement.org", "aspencer@insightmanagement.org"]  # "himel@insightpcmh.org", "himel.p.das@gmail.com", "himeldas@live.com"

if not session.MY_SALT:
    session.MY_SALT = os.urandom(8)

if not auth.id_group("admins"):
    auth.add_group("admins", "Handles assigning trainers and app managers to applications. Automatically should given"
                   "membership to all applications")

if not auth.id_group("trainers"):
    auth.add_group("trainers", "Handles many applications. Has some additional responsibilities from app managers")

if not auth.id_group("masters"):
    auth.add_group("masters", "Like admin, but bypasses permission")

if not auth.id_group("contributors"):
    auth.add_group("contributors", "The employees of a clinic that represent its corresponding application")

if not auth.id_group("app_managers"):
    auth.add_group("app_managers", "Handles data gathering")

if auth.is_logged_in():
    """Himel's role in Insight"""
    self_group = "user_%s" % auth.user.id
    if not auth.id_group(self_group):
        auth.add_group(self_group, description="Group for user %s. Created in admin panel" % self_group)
    if not auth.has_membership(self_group):
        auth.add_membership(role=self_group, user_id=auth.user.id)
    if auth.user.email in MASTER_EMAILS:
        if not auth.user.is_insight:
            db(db.auth_user.id == auth.user.id).select().last().update_record(is_insight=True)
        for _role in {"masters", "admins", "trainers", "app_managers"}: #.symmetric_difference(auth.user_groups.values()):
            auth.add_membership(role=_role, user_id=auth.user.id)
        for _role in {"observers"}:
            auth.del_membership(role=_role, user_id=auth.user.id)

APP = None
INSIGHT_ADDR = "660 Whiteplains Rd, Tarrytown, NY 10591"
IS_MASTER = auth.has_membership("masters")
IS_HIMEL = auth.has_membership("himel")
IS_ADMIN = auth.has_membership("admins")
IS_MANAGER = auth.has_membership("app_managers")
IS_TRAINER = auth.has_membership("trainers")
IS_CONTRIB = auth.has_membership("contributors")
IS_STAFF = IS_TRAINER or IS_MANAGER or IS_ADMIN
IS_TEAM = IS_STAFF or IS_CONTRIB

if IS_MASTER or IS_ADMIN:
    db.auth_user.is_insight.readable = True
    db.auth_user.is_insight.writable = True
else:
    db.auth_user.is_insight.readable = False  # make sure new users can't set this
    db.auth_user.is_insight.writable = False

# ----------------------------------------------------------------------------------------------------------------------
# Customize your APP title, subtitle and menus here
# ----------------------------------------------------------------------------------------------------------------------

response.logo = A(B('Insight', IMG(_src=URL('static','home/img/favicon.png', vars=dict(no_cache=os.urandom(9))),
                                   _style="width: 1.5em; height: 1.5em"), SPAN("PCMH")), XML('<sup>&reg;</sup>&nbsp;'),
                  _class="navbar-brand", _href=URL('default', 'index'),
                  _id="web2py-logo")
response.title = request.application.replace('_', ' ').title()
response.subtitle = ''

# ----------------------------------------------------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# ----------------------------------------------------------------------------------------------------------------------
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')

# ----------------------------------------------------------------------------------------------------------------------
# your http://google.com/analytics id
# ----------------------------------------------------------------------------------------------------------------------
response.google_analytics_id = None

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
    (SPAN(_class="glyphicon glyphicon-th-list"),
     ('default' == request.controller and 'dash' == request.function), URL('default', 'dash'), []),
]


@auth.requires(False, requires_login=True)
def ACCESS_DENIED():
    pass


if APP_ID:
    # auth.requires_membership('application_'+APP_ID)(lambda: 1)()
    if not auth.has_membership("masters"):
        if not (IS_STAFF or IS_CONTRIB) or not \
                (auth.has_permission('manage', 'application', APP_ID) or
                     auth.has_permission('train', 'application', APP_ID) or
                     auth.has_permission('contribute', 'application', APP_ID) or
                     auth.has_permission('administrate', 'application', APP_ID)):
            ACCESS_DENIED()
    APP = db(db.application.id == APP_ID).select().last()
    if not APP:  # sometimes app can be deleted, but session still holds
        ACCESS_DENIED()
elif request.controller in ["2014", "2017"]:  # do not let them access a survey without app id
    ACCESS_DENIED()

#
#
#
#
#
#
#
#
#
#

DEVELOPMENT_MENU = False


# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. remove in production
# ----------------------------------------------------------------------------------------------------------------------

def _():
    # ------------------------------------------------------------------------------------------------------------------
    # shortcuts
    # ------------------------------------------------------------------------------------------------------------------
    app = request.application
    ctr = request.controller
    # ------------------------------------------------------------------------------------------------------------------
    # useful links to internal and external resources
    # ------------------------------------------------------------------------------------------------------------------
    response.menu += [
        (T('My Sites'), False, URL('admin', 'default', 'site')),
        (T('This App'), False, '#', [
            (T('Design'), False, URL('admin', 'default', 'design/%s' % app)),
            LI(_class="divider"),
            (T('Controller'), False,
             URL(
                 'admin', 'default', 'edit/%s/controllers/%s.py' % (app, ctr))),
            (T('View'), False,
             URL(
                 'admin', 'default', 'edit/%s/views/%s' % (app, response.view))),
            (T('DB Model'), False,
             URL(
                 'admin', 'default', 'edit/%s/models/db.py' % app)),
            (T('Menu Model'), False,
             URL(
                 'admin', 'default', 'edit/%s/models/menu.py' % app)),
            (T('Config.ini'), False,
             URL(
                 'admin', 'default', 'edit/%s/private/appconfig.ini' % app)),
            (T('Layout'), False,
             URL(
                 'admin', 'default', 'edit/%s/views/layout.html' % app)),
            (T('Stylesheet'), False,
             URL(
                 'admin', 'default', 'edit/%s/static/css/web2py-bootstrap3.css' % app)),
            (T('Database'), False, URL(app, 'appadmin', 'index')),
            (T('Errors'), False, URL(
                'admin', 'default', 'errors/' + app)),
            (T('About'), False, URL(
                'admin', 'default', 'about/' + app)),
        ]),
        ('web2py.com', False, '#', [
            (T('Download'), False,
             'http://www.web2py.com/examples/default/download'),
            (T('Support'), False,
             'http://www.web2py.com/examples/default/support'),
            (T('Demo'), False, 'http://web2py.com/demo_admin'),
            (T('Quick Examples'), False,
             'http://web2py.com/examples/default/examples'),
            (T('FAQ'), False, 'http://web2py.com/AlterEgo'),
            (T('Videos'), False,
             'http://www.web2py.com/examples/default/videos/'),
            (T('Free Applications'),
             False, 'http://web2py.com/appliances'),
            (T('Plugins'), False, 'http://web2py.com/plugins'),
            (T('Recipes'), False, 'http://web2pyslices.com/'),
        ]),
        (T('Documentation'), False, '#', [
            (T('Online book'), False, 'http://www.web2py.com/book'),
            LI(_class="divider"),
            (T('Preface'), False,
             'http://www.web2py.com/book/default/chapter/00'),
            (T('Introduction'), False,
             'http://www.web2py.com/book/default/chapter/01'),
            (T('Python'), False,
             'http://www.web2py.com/book/default/chapter/02'),
            (T('Overview'), False,
             'http://www.web2py.com/book/default/chapter/03'),
            (T('The Core'), False,
             'http://www.web2py.com/book/default/chapter/04'),
            (T('The Views'), False,
             'http://www.web2py.com/book/default/chapter/05'),
            (T('Database'), False,
             'http://www.web2py.com/book/default/chapter/06'),
            (T('Forms and Validators'), False,
             'http://www.web2py.com/book/default/chapter/07'),
            (T('Email and SMS'), False,
             'http://www.web2py.com/book/default/chapter/08'),
            (T('Access Control'), False,
             'http://www.web2py.com/book/default/chapter/09'),
            (T('Services'), False,
             'http://www.web2py.com/book/default/chapter/10'),
            (T('Ajax Recipes'), False,
             'http://www.web2py.com/book/default/chapter/11'),
            (T('Components and Plugins'), False,
             'http://www.web2py.com/book/default/chapter/12'),
            (T('Deployment Recipes'), False,
             'http://www.web2py.com/book/default/chapter/13'),
            (T('Other Recipes'), False,
             'http://www.web2py.com/book/default/chapter/14'),
            (T('Helping web2py'), False,
             'http://www.web2py.com/book/default/chapter/15'),
            (T("Buy web2py's book"), False,
             'http://stores.lulu.com/web2py'),
        ]),
        (T('Community'), False, None, [
            (T('Groups'), False,
             'http://www.web2py.com/examples/default/usergroups'),
            (T('Twitter'), False, 'http://twitter.com/web2py'),
            (T('Live Chat'), False,
             'http://webchat.freenode.net/?channels=web2py'),
        ]),
    ]


if DEVELOPMENT_MENU:
    _()

if "auth" in locals():
    auth.wikimenu()

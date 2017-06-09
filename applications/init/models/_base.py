if not request.is_local:  # True if the client is localhost, False otherwise. Should work behind a proxy if the
    # proxy supports http_x_forwarded_for.
    request.requires_https()  # prevents further code execution if the request is not over HTTPS and redirects the
    # visitor to the current page over HTTPS.

APP_ID = request.get_vars["app_id"]

from string import Formatter

from gluon.storage import List, Storage

from gluon.dal import Rows

import logging

import os

logger = logging.getLogger("web2py.app.pcmh")
# The numeric values of logging levels are given in the following table.
# These are primarily of interest if you want to define your own levels,
# and need them to have specific values relative to the predefined levels.
# If you define a level with the same numeric value,
# it overwrites the predefined value; the predefined name is lost.
# Level 	Numeric value
# CRITICAL 	50
# ERROR 	40
# WARNING 	30
# INFO 	20
# DEBUG 	10
# NOTSET 	0


def _without_keys(d, *keys):
    return dict(filter(lambda key_value: key_value[0] not in keys, d.items()))


def d_tables():
    for each in db.tables:
        if not "auth_" in each:
            db(db[each].id > 0).delete()
    db.commit()


class QNA(object):
    instances = []
    reuse_form = None  # needed to keep errors in forms

    def require_show(func):  # get decorated func as first argument
        def func_wrapper(self, *args, **kwargs):  # this is the function that will replace func
            if self.show:
                return func(self, *args, **kwargs)  # run func as normal is condition met
            return False  # otherwise don't

        return func_wrapper  # this is the function that will replace func

    def __init__(self, show, table_name, question, validator=None):  # constructor
        # argument
        self.table_name = table_name
        self.table = db[table_name]
        self.question = XML(question)
        self.validator = validator
        self.show = show
        # generate
        self.form = None
        self.row = None
        self.rows = Rows()
        self.warnings = []  #
        self.form_buttons = []

        if getattr(self.__class__.reuse_form, 'table_name', None) == self.table_name:
            self.__class__.instances.append(self.__class__.reuse_form)  # keep track of instances
        else:
            self.__class__.instances.append(self)

    def set_rows(self):
        self.rows = db((self.table.id > 0) &  # https://groups.google.com/forum/#!topic/web2py/U5mqgH_BO8k
                       (self.table.application == APP_ID) &
                       (self.table.is_active == True)).select()

    def _form_process(self):
        if self.form:
            self.form.vars.application = APP_ID
            if self.form.process(onvalidation=self.validator).accepted:
                session.flash = "Answer saved!"
                redirect(URL(vars=request.get_vars))
            elif self.form.errors:
                request.reuse_form = self
                QNA.reuse_form = request.reuse_form  # form.process appears to happen before QNA.__init__

    def preprocess(self):
        """Perform tasks related to Single or Multi forms before form_process"""
        raise NotImplementedError

    def set_form_buttons(self):
        raise NotImplementedError

    @require_show  # because __init__ was not yet called, self is not the first argument here
    def process(self):
        if request.get_vars["delete"] and \
                URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["delete", "app_id"]):
            # security to prevent SQL Injection attack
            table_name, id = request.get_vars["delete"].rsplit("_", 1)  # will split table_name_1 to [table_name, 1]
            del request.get_vars["delete"]  # http://bit.ly/2gyvlqs # get rid of delete to prevent inf loop when
            # redirecting with vars=request.get_vars
            db(db[table_name].id == id).update(is_active=False)  # done - changed to active = False
            session.flash = "Deleted answer (%s) question from question #%s" % (id, table_name)
            redirect(URL(request.controller, request.function, vars=request.get_vars))  # TODO
        self.preprocess()
        self._form_process()

    @require_show
    def has_warnings(self):
        return bool(len(self.warnings))

    @require_show
    def add_warning(self, conditional, message):
        if conditional:
            self.warnings.append(XML(message))
            return True

    require_show = staticmethod(require_show)  # http://stackoverflow.com/questions/1263451/python-decorators-in-classes


class MultiQNA(QNA):
    pre_template = "<span>Submitted on {created_on}&mdash;<i>{created_by}</i> " \
                   "</span>&emsp;<span class='text-muted'>" \
                   "{note}</span><pre class='text-success'>" \
                   "<span class='text-danger pull-right'>" \
                   "&emsp;{delete_table_row}</span>%s</pre>"

    def __init__(self, multi, limit, *args, **kwargs):
        """multi: integer of number required to be answered, OR needs answer if False
           limit: turn of form submit if limit is True and multi is reached
        """
        super(MultiQNA, self).__init__(*args, **kwargs)
        self.multi = multi
        self.limit = limit

        self.template = None

        self.process()

    def preprocess(self):
        # self.rows = db(self.table.id > 0).select(orderby=~db[self.table].id,limitby=(0,self.multi))
        # https://groups.google.com/forum/#!topic/web2py/U5mqgH_BO8k
        self.set_rows()
        if self.limit == 1:
            self.row = self.rows.last()
        self.set_form_buttons()
        if len(self.rows) < self.limit:
            self.form = SQLFORM(self.table, buttons=self.form_buttons, showid=False, _action="#"+self.table_name)
            # if limit, prevent submit
        else:
            self.form = ""

    @QNA.require_show  # returns False if we're not supposed to show this form
    def needs_answer(self):
        if str(self.multi).isdigit() and self.multi <= len(self.rows):
            return False
        elif not self.multi:
            return False
        return True

    def set_template(self, template):
        self.template = template

    def set_form_buttons(self):
        submit_label = "Add Answer"
        if len(self.rows):
            submit_label = "Add Another"

        if len(self.rows) < self.multi:
            btn_class = "default"
            submit_label += " (Need %s%s)" % (self.multi, " or more" if self.limit > self.multi else "")
        else:
            btn_class = "secondary"
            submit_label += " (If Needed)"

        self.form_buttons.append(TAG.button(submit_label, _type="submit", _class="btn btn-%s pull-right" % btn_class))

    @classmethod
    def _render_template(cls, table_name, rows, template, trash=True):
        """HAPPENS BEFORE SET_TEMPLATE"""
        for row in rows:

            keys = filter(lambda key: key, [i[1] for i in Formatter().parse(template)])
            # filter because we get Nones # http://stackoverflow.com/questions/13037401/get-keys-from-template

            logger.warn("Possible source of infinite loop, for some reason it acts weird when using {created_by}"
                        " (reference object)")  # fixme

            def _print_row_delete_icon(func):
                def inner(key):
                    if trash and key == "delete_table_row":
                        return key, A(SPAN(_class="glyphicon glyphicon-trash hidden-print"), _class="text-danger",
                                      _href="#",
                                      _onClick="if(confirm('Are you sure?')){parent.location='%s'}" %
                                               URL(vars=dict([('delete', table_name+"_%s" % row.id)] +
                                                             request.get_vars.items()),
                                                   hmac_key=MY_KEY, salt=session.MY_SALT,
                                                   hash_vars=["delete", "app_id"]),
                                      _title="Delete this answer"
                                      )
                    return func(key)
                return inner

            def _print_auth_user(func):
                def inner(key):
                    if key in ["created_by", "modified_by"]:
                        auth_user = db(db.auth_user.id == row[key]).select().last()
                        # memberships = ", ".join(map(lambda m: m.auth_group.role.capitalize().replace("_", " ")[:-1],
                        #                             db((db.auth_membership.user_id == auth_user.id) &
                        #                                (db.auth_membership.group_id == db.auth_group.id) &
                        #                                (db.auth_group.role.belongs(["admins", "app_managers",
                        #                                                             "trainers", "contributors"]))
                        #                                ).select()))
                        return key, "%s %s (%s)" % (auth_user.first_name.capitalize(), auth_user.last_name.capitalize(),
                                                    auth_user.id)
                    return func(key)
                return inner

            def _print_file(func):
                def inner(key):
                    if key == "choose_file":
                        return key, A(row["file_description"],
                                      _href=URL("init", request.controller, "download",
                                                args=[row["choose_file"]],
                                                vars=dict(app_id=APP_ID)
                                                ))
                    return func(key)
                return inner

            @_print_file
            @_print_row_delete_icon
            @_print_auth_user
            def _print_comma_list(key):  # join with commas if object is list-like (python 2 only)
                # http://stackoverflow.com/questions/1835018/python-check-if-an-object-is-a-list-or-tuple-but-not-string
                # assert row.get(key), "Could not find '%s' in row" % key
                if not hasattr(row[key], '__iter__'):
                    return key, row[key]  # needed to do **vars for string.format
                else:
                    return key, ", ".join(map(lambda e: str(e), row[key]))
                    # the map is needed to convert int/float to str

            logger.warning("can get value error invalid conversion specification due to None type datetime")
            # x=map(_print_comma_list, keys)
            yield XML(template.format(
                **dict(
                    map(_print_comma_list, keys)  #
                )))  # would look like self.template.format(name="Jon", ...)

    def render_template(self):
        assert self.template, "template was not set for #%s" % self.table_name
        return self._render_template(self.table_name, self.rows, self.pre_template % self.template)


class CryptQNA(MultiQNA):
    pre_template = "<span>Encrypted on {created_on}&mdash;<i>{created_by}</i> " \
                   "</span>&emsp;<span class='text-muted'>" \
                   "{note}</span><pre class='text-success'>" \
                   "<span class='text-danger pull-right'>" \
                   "&emsp;{delete_table_row}</span>%s</pre>"

    def __init__(self, *args, **kwargs):
        super(CryptQNA, self).__init__(*args, **kwargs)

    def preprocess(self):
        # self.rows = db(self.table.id > 0).select(orderby=~db[self.table].id,limitby=(0,self.multi))
        # https://groups.google.com/forum/#!topic/web2py/U5mqgH_BO8k
        self.validator = _on_validation_crypt(self.table_name)

        self.set_rows()

        self.set_form_buttons()

        if len(self.rows) < self.limit:
            self.form = SQLFORM.factory(*_fake_db[self.table_name], buttons=self.form_buttons)
            # if limit, prevent submit
        else:
            self.form = ""

    def set_form_buttons(self):
        submit_label = "Add Answer"
        if len(self.rows):
            submit_label = "Add Another"

        if len(self.rows) < self.multi:
            btn_class = "default"
            submit_label += " (Need %s%s)" % (self.multi, " or more" if self.limit > self.multi else "")
        else:
            btn_class = "secondary"
            submit_label += " (If Needed)"

        submit_label = SPAN(SPAN(_class='glyphicon glyphicon-lock'), " ", submit_label)

        self.form_buttons.append(TAG.button(submit_label, _title="This answer will be GPG encrypted",
                                            _type="submit", _class="btn btn-%s pull-right" % btn_class))


def mailer(user_ids, subject, message, summary, action_url, call_to_action):
    users = db(db.auth_user.id.belongs(user_ids)).select()
    assert users, "Expected users before email!"
    for user in users:
        first_name = user.first_name
        email = user.email
        rendered = response.render(os.path.join("templates", "email.html"),
                                   dict(summary=summary, first_name=first_name, message=message, action_url=action_url,
                                        call_to_action=call_to_action)
                                   )
        mail.send(to=[email],
                  subject=subject,
                  message=rendered)


def DOC_HEADER():
    """:returns:
        PRACTICE_NAME=app.practice_name,
        PRACTICE_CITY=app.practice_city,
        PRACTICE_STREET=street,
        PRACTICE_STATE=app.practice_state,
        PRACTICE_NUMBER=phone,
        PRACTICE_FAX=app.practice_fax,
        PRACTICE_ZIP=app.practice_zip,
        DATE=request.now.strftime("%m/%d/%y")
    """
    app = db(db.application.id == APP_ID).select().last()
    street = ("%s %s" % (app.practice_address_line_1, app.practice_address_line_2) if app.practice_address_line_2 else
              app.practice_address_line_1)
    phone = ("%s ext: %s" % (app.practice_phone, app.practice_phone_extension) if app.practice_phone_extension else
             app.practice_phone)
    return dict(
        PRACTICE_NAME=app.practice_name,
        PRACTICE_CITY=app.practice_city,
        PRACTICE_STREET=street,
        PRACTICE_STATE=app.practice_state,
        PRACTICE_NUMBER=phone,
        PRACTICE_FAX=app.practice_fax,
        PRACTICE_ZIP=app.practice_zip,
        DATE=request.now.strftime("%m/%d/%y")
    )


def CAROUSEL(_id, values):
    """
    :param _id: The table ID number
    :param values: [(title, caption, src)]
    :return: A carousel string

    <div id="carouselExampleIndicators" class="carousel slide" data-ride="carousel">
      <ol class="carousel-indicators">
        <li data-target="#carouselExampleIndicators" data-slide-to="0" class="active"></li>
        <li data-target="#carouselExampleIndicators" data-slide-to="1"></li>
        <li data-target="#carouselExampleIndicators" data-slide-to="2"></li>
      </ol>
      <div class="carousel-inner" role="listbox">
        <div class="carousel-item active">
          <img class="d-block img-fluid" src="..." alt="First slide">
        </div>
        <div class="carousel-item">
          <img class="d-block img-fluid" src="..." alt="Second slide">
        </div>
        <div class="carousel-item">
          <img class="d-block img-fluid" src="..." alt="Third slide">
        </div>
      </div>
      <a class="carousel-control-prev" href="#carouselExampleIndicators" role="button" data-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="sr-only">Previous</span>
      </a>
      <a class="carousel-control-next" href="#carouselExampleIndicators" role="button" data-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="sr-only">Next</span>
      </a>
    </div>
    """
    _id = "carousel_" + _id
    targets = []
    items = []
    for i, value in enumerate(values):
        title, caption, src = value
        targets.append(LI(**
                          dict({"_data-target": "#"+_id, "_data-slide-to": i}.items()
                               + ({} if i == 0 else {"_class": "active"}).items())
                          )
                       )
        items.append(DIV(
            IMG(_src=src, _class="img-thumbnail"),
            DIV(H3(title), P(caption), _class="carousel-caption",
                _style="background: rgba(0,0,0,0.5); border-radius: 20px; margin: 5px;"
                ),
            _class="item%s" % ("" if i != 0 else " active"),
        ))

    inner = DIV(*items, _class="carousel-inner", _role="listbox")
    prev = indicators = _next = ""
    if len(values) > 1:
        indicators = OL(*targets, _class="carousel-indicators")
        prev = A(SPAN(_class="glyphicon glyphicon-chevron-left"), _class="left carousel-control",
                 _role="button",
                 _href="#"+_id, **{"_data-slide": "prev"}
                 )
        _next = A(SPAN(_class="glyphicon glyphicon-chevron-right"), _class="right carousel-control",
                  _role="button",
                  _href="#"+_id, **{"_data-slide": "next"}
                  )  # http://bit.ly/2rhaCQi
    return DIV(indicators, inner, prev, _next, _id=_id, _class="carousel slide",
               **{"_data-ride": "carousel"})

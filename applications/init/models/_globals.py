if not request.is_local:  # True if the client is localhost, False otherwise. Should work behind a proxy if the proxy supports http_x_forwarded_for.
    request.requires_https()  # prevents further code execution if the request is not over HTTPS and redirects the visitor to the current page over HTTPS.

from string import Formatter
from gluon.storage import Storage
import logging
import os

logger = logging.getLogger("web2py.app.pcmh")

"""
The numeric values of logging levels are given in the following table.
These are primarily of interest if you want to define your own levels,
and need them to have specific values relative to the predefined levels.
If you define a level with the same numeric value,
it overwrites the predefined value; the predefined name is lost.
Level 	Numeric value
CRITICAL 	50
ERROR 	40
WARNING 	30
INFO 	20
DEBUG 	10
NOTSET 	0
"""

_list_of_states = ["NY", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
                   "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                   "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                   "NM", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                   "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

_days_of_the_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

_day_of_week_field = lambda label=None, comment=None: \
    Field("day_of_the_week",
          requires=IS_IN_SET(_days_of_the_week, zero=None),
          label=label,
          comment=comment
    )

_days_of_week_field = lambda label=None, comment=None: \
    Field("days_of_the_week", 'list:string',
          requires=[IS_IN_SET(_days_of_the_week, zero=None, multiple=True),
                    IS_NOT_EMPTY()],
          widget=SQLFORM.widgets.multiple.widget,
          label=label,
          comment=comment
    )

_am_pm_time_validator = IS_TIME("Enter time as HH:MM [AM/PM]")


def _validate_start_end_time(form, start_field_name="start_time", end_field_name="end_time"):
    # get the actual datetime.time object and compare
    if form.vars[start_field_name] > form.vars[end_field_name]:
        form.errors[start_field_name] = "Start time cannot be after the end time!"
        form.errors[end_field_name] = "End time cannot be before the start time!"


def d_tables():
    for each in db.tables:
        if not "auth_" in each:
            db(db[each].id > 0).delete()
    db.commit()

class QNA(object):
    instances = []

    def require_show(func):  # get decorated func as first argument
        def func_wrapper(self, *args, **kwargs):  # this is the function that will replace func
            if self.show:
                return func(self, *args, **kwargs)  # run func as normal is condition met
            return False  # otherwise don't

        return func_wrapper  # this is the function that will replace func

    def __init__(self, show, table_name, question, validator=None):  # constructor
        self.__class__.instances.append(self)  # keep track of instances
        #argument
        self.table_name = table_name
        self.table = db[table_name]
        self.question = XML(question)
        self.validator = validator
        self.show = show
        #generate
        self.form = None
        self.row = None
        self.rows = []
        self.warnings = []  #
        self.form_buttons = []

    def _form_process(self):
        if self.form and self.form.process(onvalidation=self.validator).accepted:
            session.flash = "Answer saved!"
            redirect(URL(vars=request.get_vars))

    def preprocess(self):
        """Perform tasks related to Single or Multi forms before form_process"""
        raise NotImplementedError

    def set_form_buttons(self):
        raise NotImplementedError

    @require_show  # because __init__ was not yet called, self is not the first argument here
    def process(self):
        if request.get_vars["delete"] and URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT or "", hash_vars=["delete", "app_id"]):  # security to prevent SQL Injection attack
            table_name, id = request.get_vars["delete"].rsplit("_", 1)  # will split table_name_1 to [table_name, 1]
            del request.get_vars["delete"]  # http://bit.ly/2gyvlqs # get rid of delete to prevent inf loop when redirecting with vars=request.get_vars
            db(db[table_name].id == id).delete()  # change to active = False
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
            self.warnings.append(XML(T(message)))
            return True

    require_show = staticmethod(require_show)  # http://stackoverflow.com/questions/1263451/python-decorators-in-classes


class MultiQNA(QNA):
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
        # self.rows = db(self.table.id > 0).select(orderby=~db[self.table].id,limitby=(0,self.multi))  # https://groups.google.com/forum/#!topic/web2py/U5mqgH_BO8k
        self.rows = db(self.table.id > 0).select()  # https://groups.google.com/forum/#!topic/web2py/U5mqgH_BO8k
        if self.limit == 1:
            self.row = self.rows.last()
        self.set_form_buttons()
        #self.form = MultiSQLFORM(self.table_name, self.rows, self.multi, _action="#"+self.table_name)  # if limit, prevent submit
        if len(self.rows) < self.limit:
            self.form = SQLFORM(self.table, buttons=self.form_buttons, showid=False, _action="#"+self.table_name)  # if limit, prevent submit
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
        self.template = "<span>Submitted on {created_on}&mdash;<i>{created_by}</i> </span>&emsp;<span class='text-muted'>" \
                        "{note}</span><pre class='text-success'>" \
                        "<span class='text-danger pull-right'>" \
                        "&emsp;{delete_table_row}" \
                        "</span>" \
                        "%s</pre>" % template

    def set_form_buttons(self):
        submit_label = "Add Answer"
        if len(self.rows):
            submit_label = T("Add Another")
        else:
            self.clear_button = ""

        if len(self.rows) < self.multi:
            btn_class = "warning"
        else:
            btn_class = "primary"

        self.form_buttons.append(TAG.button(submit_label, _type="submit", _class="btn btn-%s pull-right" % btn_class))

    def render_template(self):
        for row in self.rows:
            keys = filter(lambda key: key, [i[1] for i in Formatter().parse(self.template)])  #filter because we get Nones # http://stackoverflow.com/questions/13037401/get-keys-from-template

            logger.warn("Possible source of infinite loop, for some reason it acts weird when using {created_by}"
                        " (reference object)")  # fixme

            def _print_row_delete_icon(func):
                def inner(key):
                    if key == "delete_table_row":
                        return key, A(SPAN(_class="glyphicon glyphicon-trash"), _class="text-danger",
                                      _href="#",
                                      _onClick="if(confirm('Clear entry?')){parent.location='%s'}" %
                                                URL(vars=dict([('delete', self.table_name+"_%s" % row.id)] +
                                                              request.get_vars.items()),
                                                    hmac_key=MY_KEY, salt=session.MY_SALT or "",
                                                    hash_vars=["delete", "app_id"]),
                                      )
                    return func(key)
                return inner

            def _print_auth_user(func):
                def inner(key):
                    if key in ["created_by", "modified_by"]:
                        auth_user = db(db.auth_user.id == row[key]).select().last()
                        memberships = ", ".join(map(lambda m: m.auth_group.role.capitalize().replace("_", " ")[:-1],
                                                    db((db.auth_membership.user_id == auth_user.id) &
                                                       (db.auth_membership.group_id == db.auth_group.id) &
                                                       (db.auth_group.role.belongs(["admins", "app_managers",
                                                                                    "trainers", "contributors"]))
                                                       ).select()))
                        return key, "%s %s (%s) (%s)" % (auth_user.first_name.capitalize(),
                                                         auth_user.last_name.capitalize(),
                                                         auth_user.id, memberships)
                    return func(key)
                return inner

            @_print_row_delete_icon
            @_print_auth_user
            def _print_comma_list(key):  #join with commas if object is list-like (python 2 only) http://stackoverflow.com/questions/1835018/python-check-if-an-object-is-a-list-or-tuple-but-not-string
                if not hasattr(row[key], '__iter__'):
                    return key, row[key]  # needed to do **vars for string.format
                else:
                    return key, ", ".join(row[key])

            yield XML(self.template.format(
                **dict(
                    map(_print_comma_list, keys)  #
                )))  # would look like self.template.format(name="Jon", ...)

'''
class SingleQNA(QNA):

    def __init__(self, *args, **kwargs):
        super(SingleQNA, self).__init__(*args, **kwargs)
        self.process()

    def preprocess(self):
        """make form editable"""
        self.row = db(self.table.id > 0).select().last()
        self.set_form_buttons()
        self.form = SQLFORM(self.table, record=self.row, buttons=self.form_buttons, showid=False, _action="#"+self.table_name)

    def set_form_buttons(self):
        submit_label = "Submit Answer"
        btn_class = "warning"

        if bool(self.row):
            submit_label = T("Change Answer")
            btn_class = "primary"
        else:
            self.clear_button = ""

        self.form_buttons.append(TAG.button(submit_label, _type="submit", _class="btn btn-%s pull-right" % btn_class))


    @QNA.require_show
    def needs_answer(self):
        if self.row:
            return False
        return True
'''

class CryptQNA(MultiQNA):

    def __init__(self, *args, **kwargs):
        super(CryptQNA, self).__init__(*args, **kwargs)

    def preprocess(self):
        # self.rows = db(self.table.id > 0).select(orderby=~db[self.table].id,limitby=(0,self.multi))  # https://groups.google.com/forum/#!topic/web2py/U5mqgH_BO8k
        self.validator = _on_validation_crypt(self.table_name)

        self.rows = db(self.table.id > 0).select()  # https://groups.google.com/forum/#!topic/web2py/U5mqgH_BO8k

        self.set_form_buttons()

        if len(self.rows) < self.limit:
            self.form = SQLFORM.factory(*_fake_db[self.table_name], buttons=self.form_buttons)  # if limit, prevent submit
        else:
            self.form = ""

    def set_form_buttons(self):
        submit_label = "Add Answer"
        if len(self.rows):
            submit_label = T("Add Another")
        else:
            self.clear_button = ""

        if len(self.rows) < self.multi:
            btn_class = "warning"
        else:
            btn_class = "primary"

        self.form_buttons.append(TAG.button(submit_label, _type="submit", _class="btn btn-%s pull-right" % btn_class))

    def set_template(self, template):
        self.template = "<span>Encrypted on {created_on}&mdash;<i>{created_by}</i></span>" \
                        "<pre class='text-success'>" \
                        "<span class='text-danger pull-right'>" \
                        "&emsp;{delete_table_row}" \
                        "</span>" \
                        "%s</pre>" % template
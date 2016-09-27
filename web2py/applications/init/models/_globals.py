from string import Formatter

_telephone_field_validator = IS_MATCH("^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}$")
_note_field = Field("note", label=XML("<span class='text-muted'>Note to Trainer (Optional)</span>"))
_yes_no_field_default = Field("please_choose", requires=IS_IN_SET([("Y", "Yes"), ("N", "No")]))
_day_of_week_field = lambda label=None: Field("day_of_the_week",
                                          requires=IS_IN_SET(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                                                              "Saturday", "Sunday"], zero=None),
                                          label=label
                                          )
_am_pm_time_validator = IS_TIME("Enter time as HH:MM [AM/PM]")



def _validate_filename(form):
    form.vars.filename = request.vars.upload.filename


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


class MixinSQLFORM(object):
    def __init__(self, table_name):
        self.buttons = []
        self.table_name = table_name

    def insert_clear_btn(self):
        self.buttons.insert(0, TAG.button('Clear', _type="button", _class="btn btn-info pull-right",
                                     _onClick="if(confirm('Clear entry?')){parent.location='%s'}" %
                                              URL(vars=dict(delete=self.table_name))))  # confirm redirect


class SingleSQLFORM(SQLFORM, MixinSQLFORM):
    def __init__(self, table_name, row, *args, **kwargs):
        MixinSQLFORM.__init__(self, table_name)

        submit_label = "Submit Answer"
        btn_class = "warning"

        if bool(row):
            submit_label = T("Change Answer")
            btn_class = "primary"

        self.buttons.append(TAG.button(submit_label, _type="submit", _class="btn btn-%s pull-right"%btn_class))

        if bool(row):
            self.insert_clear_btn()

        super(self.__class__, self).__init__(db[table_name], record=row, buttons=self.buttons, showid=False, *args, **kwargs)


class MultiSQLFORM(SQLFORM, MixinSQLFORM):
    def __init__(self, table_name, rows, multi, *args, **kwargs):
        MixinSQLFORM.__init__(self, table_name)

        submit_label = "Add Answer"
        if len(rows):
            submit_label = T("Add Another")

        if len(rows) < multi:
            btn_class = "warning"
        else:
            btn_class = "primary"

        self.buttons.append(TAG.button(submit_label, _type="submit", _class="btn btn-%s pull-right"%btn_class))

        if len(rows):
            self.insert_clear_btn()

        super(self.__class__, self).__init__(db[table_name],
            #record=row,
            #submit_button=T('Change Answer') if bool(row) else T("Submit Answer"),
            buttons=self.buttons,
            showid=False, *args, **kwargs)


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

    def _form_process(self):
        if self.form.process(onvalidation=self.validator).accepted:
            session.flash = "Answer saved!"
            redirect(URL())

    def preprocess(self):
        """Perform tasks related to Single or Multi forms before form_process"""
        raise NotImplementedError

    @require_show  # because __init__ was not yet called, self is not the first argument here
    def process(self):
        if request.vars["delete"] == self.table_name:  # security to prevent SQL Injection attach
            db(db[self.table_name].id > 0).delete()  # change to active = False
            session.flash = "deleted question %s"%self.table_name
            redirect(URL())
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
    def __init__(self, multi, limit, *args, **kwargs):
        """multi: integer of number required to be answered, OR needs answer if False
           limit: turn of form submit if limit is True and multi is reached
        """
        super(self.__class__, self).__init__(*args, **kwargs)
        self.multi = multi
        self.limit = limit
        self.template = None

        self.process()

    def preprocess(self):
        # self.rows = db(self.table.id > 0).select(orderby=~db[self.table].id,limitby=(0,self.multi))  # https://groups.google.com/forum/#!topic/web2py/U5mqgH_BO8k
        self.rows = db(self.table.id > 0).select()  # https://groups.google.com/forum/#!topic/web2py/U5mqgH_BO8k
        self.form = MultiSQLFORM(self.table_name, self.rows, self.multi)  # if limit, prevent submit

    @QNA.require_show  # returns False if we're not supposed to show this form
    def needs_answer(self):
        if str(self.multi).isdigit() and self.multi <= len(self.rows):
            return False
        elif not self.multi:
            return False
        return True

    def set_template(self, template):
        self.template = template

    def render_template(self):
        for row in self.rows:
            keys = filter(lambda key: key, [i[1] for i in Formatter().parse(self.template)])  #filter because we get Nones # http://stackoverflow.com/questions/13037401/get-keys-from-template
            yield XML(self.template.format(
                **dict(
                    map(lambda key: (key, row[key]), keys)
                )))  # would look like self.template.format(name="Jon", ...)


class SingleQNA(QNA):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.process()

    def preprocess(self):
        """make form editable"""
        self.row = db(self.table.id > 0).select().last()
        self.form = SingleSQLFORM(self.table_name, self.row)

    @QNA.require_show
    def needs_answer(self):
        if self.row:
            return False
        return True



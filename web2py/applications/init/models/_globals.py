_telephone_field_validator = IS_MATCH("^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}$")
_note_field = Field("note", label=XML("<span class='text-muted'>Note to Trainer (Optional)</span>"))
_yes_no_field_default = Field("please_choose", requires=IS_IN_SET([("Y", "Yes"), ("N", "No")]))

def dtable():
    for each in db.tables:
        if not "auth_" in each:
            db(db[each].id > 0).delete()
    db.commit()

class SQLFORM_ANSWER(SQLFORM):
    def __init__(self, table, row, rows, *args, **kwargs):

        submit_label = "Submit Answer"
        if bool(row):
            submit_label = T("Change Answer")
        elif len(rows):
            submit_label = T("Add Another")

        buttons = [TAG.button(submit_label, _type="submit", _class="btn btn-primary pull-right")]

        if len(rows) > 0 or bool(row):
            buttons.insert(0, TAG.button('Clear', _type="button", _class="btn btn-info pull-right",
                            _onClick="if(confirm('Clear entry?')){parent.location='%s'}" % URL()))  # confirm redirect

        super(self.__class__, self).__init__(table,
            record=row,
            #submit_button=T('Change Answer') if bool(row) else T("Submit Answer"),
            buttons=buttons,
            showid=False, *args, **kwargs)


def MISSING_ANSWERS(*args):  # if form is true AND row is true, then question has been answered
    needs_answering = []
    for answered, form in args:
        needs_answering.append(not (not form or (form and answered)))
    return any(needs_answering)


def INCORRECT_ANSWERS(*forms):
    needs_fixing = []
    for form in filter(lambda x: bool(x), forms):
        needs_fixing.append(form.warnings)
    return any(needs_fixing)


def FORM_PROCESSOR_GENERIC(condition_to_show, question_table, validator=None, multi=False):
    form = None
    result = None  # keep None here in case previous answer changes
    results = []
    if condition_to_show:
        if not multi:
            result = db(question_table.id > 0).select().last()
            form = SQLFORM_ANSWER(question_table, result)
        else:
            results = db(question_table.id > 0).select()
            form = SQLFORM_ANSWER(question_table, None)
        if form.process(onvalidation=validator).accepted:
            session.flash = "Answer saved!"
            redirect(URL())
    return (result if not multi else results), form

class question_and_answer():
    instances = []

    def __init__(self, show, table, question, validator=None, multi=1):

        self.table = table
        self.question = question
        self.validator = validator
        self.multi = multi
        self.show = show

        self.form = None
        self.row = None
        self.rows = []
        self.warnings = []

        self.__class__.instances.append(self)  # keep track of instances

        if not show:
            return

        if multi > 1:
            self.preprocess_multi()
        else:
            self.preprocess_single()

        self.form_process()

    def preprocess_single(self):
        """make form editable"""
        self.row = db(self.table.id > 0).select().last()
        self.form = SQLFORM_ANSWER(self.table, self.row, [])

    def preprocess_multi(self):
        self.rows = db(self.table.id > 0).select(orderby=~db[self.table].id,limitby=(0,self.multi))  # https://groups.google.com/forum/#!topic/web2py/U5mqgH_BO8k
        self.form = SQLFORM_ANSWER(self.table, None, self.rows)

    def form_process(self):
        if self.form.process(onvalidation=self.validator).accepted:
            session.flash = "Answer saved!"
            redirect(URL())

    def has_warnings(self):
        if not self.form:
            return False
        return bool(len(self.warnings))

    def addWarnings(self, conditional, message):
        if self.form and conditional:
            self.warnings.append(message)

    def needs_answer(self):
        if not self.show:
            return False

        if self.multi < 2 and self.row:
            return False

        if self.multi == len(self.rows):
            return False

        return True


def VALIDATE_FILENAME(form):
    form.vars.filename = request.vars.upload.filename
_telephone_field_validator = IS_MATCH("^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}$")
_note_field = Field("note", label=XML("<span class='text-muted'>Note to Trainer (Optional)</span>"))
_yes_no_field_default = Field("please_choose", requires=IS_IN_SET([("Y", "Yes"), ("N", "No")]))

class SQLFORM_ANSWER(SQLFORM):
    def __init__(self, table, row_object, *args, **kwargs):
        super(self.__class__, self).__init__(table,
            record=row_object,
            submit_button=T('Change Answer') if bool(row_object) else T("Submit Answer"),
            showid=False, *args, **kwargs)

def MISSING_ANSWERS(*args):  #
    needs_answering = []
    for row, form in args:
        needs_answering.append(not (not form or (form and row)))
    return any(needs_answering)


def FORM_PROCESSOR_GENERIC(condition_to_show, table):
    row = None  # keep None here in case previous answer changes
    form = None
    if condition_to_show:
        row = db(table.id > 0).select().last()
        form = SQLFORM_ANSWER(table, row)
        if form.process().accepted:
            session.flash = "Answer saved!"
            redirect(URL())
    return row, form

def VALIDATE_FILENAME(form):
    form.vars.filename = request.vars.upload.filename
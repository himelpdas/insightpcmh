def practice_information():
    answer_form = SQLFORM(db.PCMH_Primary_Contact)
    if answer_form.process().accepted:
        response.flash = "Hello Atif"
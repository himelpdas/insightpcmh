@auth.requires(URL.verify(request,
                          hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "table_name", "template"]))
def history():
    rows = db(db[request.get_vars['table_name']].application == request.get_vars["app_id"]).select()

    pre_template = "<span class='text-muted'>Submitted on {created_on}&mdash;<i>{created_by}</i> " \
                   "</span>&emsp;<span class='text-muted'>{note}</span><pre>%s</pre>"

    rendered = MultiQNA._render_template(request.get_vars['table_name'], rows,
                                         template=pre_template % request.get_vars["template"],
                                         trash=False)
    return dict(rendered=[XML("<span class='text-danger'>No history found!</span>")] if not rows else rendered)


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "mark", "redir"]))
def mark_as():
    table_name = request.get_vars["mark"]
    redir = request.get_vars["redir"]
    complete_set = set(APP.force_complete)
    update = True
    if "remove" == request.args(0):
        try:
            complete_set.remove(table_name)
            session.flash = "Unmarked #%s!" % table_name.upper()
        except KeyError:
            session.flash = "Already unmarked #%s!" % table_name.upper()
            update = False
    else:
        complete_set.add(table_name)
        session.flash = "Marked #%s as complete!" % table_name.lower()
    if update:
        db(db.application.id == APP_ID).update(force_complete=list(complete_set))

    redirect(URL(c="2014", f=redir, vars=dict(app_id=APP_ID)))
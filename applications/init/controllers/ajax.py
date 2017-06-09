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

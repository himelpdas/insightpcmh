response.view = os.path.join("templates", "survey_extend.html")  # http://stackoverflow.com/questions/8750723/is-it-possible-to-change-a-web2py-view-on-the-fly
response.title = "PCMH 1"


#@auth.requires(URL.verify(request, hash_vars=["app_id"], hmac_key=MY_KEY), requires_login=True)


def index():
    redirect(URL("a", vars=request.vars))

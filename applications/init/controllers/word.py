from gluon import contenttype

# response.headers['Content-Type'] = contenttype.CONTENT_TYPE['.doc']
response.headers['Content-Type'] = 'application/msword'


# todo - this has no RBAC
def index():
    app = db(db.application.id == APP_ID).select().last()
    street = ("%s %s" % (app.practice_address_line_1, app.practice_address_line_2) if app.practice_address_line_2 else
              app.practice_address_line_1)
    phone = ("%s ext: %s" % (app.practice_phone, app.practice_phone_extension) if app.practice_phone_extension else
              app.practice_phone)
    return dict(
        PRACTICE_NAME = app.practice_name,
        PRACTICE_CITY = app.practice_city,
        PRACTICE_STREET = street,
        PRACTICE_STATE = app.practice_state,
        PRACTICE_NUMBER = phone,
        PRACTICE_FAX = app.practice_fax,
        PRACTICE_ZIP = app.practice_zip,
        DATE = request.now.strftime("%m/%d/%y")
    )


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["type", "app_id"]))
# security to prevent SQL Injection attack
def tracking_chart():
    return dict(_type=request.get_vars["type"], **index())


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"]))
def discharge_poster():
    return index()


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"]))
def same_day_training_generic():
    return dict(EMR_NAME=APP.emr, **index())

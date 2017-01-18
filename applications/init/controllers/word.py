from gluon import contenttype

response.headers['Content-Type'] = contenttype.CONTENT_TYPE['.doc']


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


def referral_tracking_chart():
    return index()

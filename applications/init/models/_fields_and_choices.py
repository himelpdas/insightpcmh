LIST_OF_STATES = ["NY", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
                   "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                   "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                   "NM", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                   "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

EMRS = ['Other', "Amazing Charts", 'eClinicalWorks', 'Health Fusion', 'MDLand iClinic', "Practice Fusion"]
REMOTE_EMRS = EMRS[1:2]
CLOUD_EMRS = EMRS[2:]
EMRS = ["Practice Fusion"]

DAYS_OF_THE_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# PHONE_VALIDATOR = requires = IS_MATCH('\([0-9][0-9][0-9]\)[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]',
PHONE_VALIDATOR = requires = IS_MATCH('^\(*\+*[1-9]{0,3}\)*-*[1-9]{0,3}[-. /]*\(*[2-9]\d{2}\)*[-. /]*\d{3}[-. /]*\d{4} *e*x*t*\.* *\d{0,4}$',
                                                 error_message='Invalid telephone number')

NOTE_FIELD = Field("note", label=XML("<span class='text-muted'>Note</span>"), comment="Optional")

YES_NO_FIELD = Field("please_choose", requires=IS_IN_SET(["Yes", "No / Not sure / Need help"]),
                              comment=XML("<span class='visible-print-inline'>Yes or No.</span>"))

NOT_YES = ["No / Not sure / Need help"]


DAY_FIELD = lambda label=None, comment=None: \
    Field("day_of_the_week",
          requires=IS_IN_SET(DAYS_OF_THE_WEEK, zero=None),
          label=label,
          comment=comment
    )


DAYS_OF_WEEK_FIELD = lambda label=None, comment=None: \
    Field("days_of_the_week", 'list:string',
          requires=[IS_IN_SET(DAYS_OF_THE_WEEK, zero=None, multiple=True),
                    IS_NOT_EMPTY()],
          widget=SQLFORM.widgets.multiple.widget,
          label=label,
          comment=comment
    )

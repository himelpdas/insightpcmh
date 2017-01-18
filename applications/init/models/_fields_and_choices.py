_list_of_states = ["NY", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
                   "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                   "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                   "NM", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                   "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

EMRS = ['Other', "Amazing Charts", 'eClinicalWorks', 'Health Fusion', 'MDLand iClinic', "Practice Fusion"]
REMOTE_EMRS = EMRS[1:2]
CLOUD_EMRS = EMRS[2:]

_days_of_the_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

_telephone_field_validator = requires = IS_MATCH('\([0-9][0-9][0-9]\)[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]',
                                                 error_message='Use the format (123)456-7890 (no spaces)')

_note_field = Field("note", label=XML("<span class='text-muted'>Note</span>"), comment="Optional")

_yes_no_field_default = Field("please_choose", requires=IS_IN_SET(["Yes", "No", "Not sure"]),
                              comment=XML("<span class='visible-print-inline'>Yes or No.</span>"))

NOT_YES = ["No", "Not sure"]

_day_of_week_field = lambda label=None, comment=None: \
    Field("day_of_the_week",
          requires=IS_IN_SET(_days_of_the_week, zero=None),
          label=label,
          comment=comment
    )


_days_of_week_field = lambda label=None, comment=None: \
    Field("days_of_the_week", 'list:string',
          requires=[IS_IN_SET(_days_of_the_week, zero=None, multiple=True),
                    IS_NOT_EMPTY()],
          widget=SQLFORM.widgets.multiple.widget,
          label=label,
          comment=comment
    )

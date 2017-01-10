db.define_table('referral_blurb',
                Field("application", 'reference application', readable=False, writable=False),
                _yes_no_field_default,
                _note_field,
                )
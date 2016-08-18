import random

def PCMH_1A_1():

    return dict(
        practice_name="Parkchester Medical PC",
        sameday_visits_percent="30%",
        prebooked_visits_percent="70%",
        accute_illnesses_seen_within=24,
    )

def testing():
    #response.headers['Content-Type'] = 'application/octet-stream'  # will force download if using .xml extension or else browser will just view
    #response.headers['Content-Type'] = 'application/msword'  # will save as doc if using .xml extension, commented out because we changed the .xml template to .doc, but still using wordprocessingml http://stackoverflow.com/questions/4212861/what-is-a-correct-mime-type-for-docx-pptx-etc
    #response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document  # will save as .docx which will not work with word 2003 xml
    return dict(PRACTICE_NAME="Testing Practice")

def ADHD_screening_letter():
    return (dict(
        PRACTICE_NAME="Jothianandan Kanthimathi MD",
        DOCTOR_NAME="Dr. Jothi",
        PRACTICE_NUMBER="917-698-8536",
        PRACTICE_FAX="917-698-8537",
        PRACTICE_STREET="660 White Plains Rd.",
        PRACTICE_CITY="Tarrytown",
        PRACTICE_STATE="NY",
        PRACTICE_ZIP="11101",
        RAND_LETTER_1=chr(random.randint(65, 90)),
        RAND_PAD="0"*random.randint(10, 20),
        RAND_LETTER_2=chr(random.randint(65, 90)),
        PATIENT_GENDER_PRONOUN="her" if random.choice([True,False]) else "his",
    ))
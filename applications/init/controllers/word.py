from gluon import contenttype
import docx
from cStringIO import StringIO

# response.headers['Content-Type'] = contenttype.CONTENT_TYPE['.doc']
if not request.extension.lower() == 'doc':
    redirect(URL(f=request.function + ".doc", args=request.args, vars=request.get_vars))
response.headers['Content-Type'] = 'application/msword'


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["type", "app_id"]))
# security to prevent SQL Injection attack
def tracking_chart():
    return dict(_type=request.get_vars["type"], **DOC_HEADER())


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"]))
# security to prevent SQL Injection attack
def telephone_chart():
    return dict(_type=request.get_vars["type"], **DOC_HEADER())


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"]))
def discharge_poster():
    return DOC_HEADER()


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"]))
def same_day_training_generic():
    return dict(EMR_NAME=APP.emr, **DOC_HEADER())


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"]))
def er_ip_log():
    return dict(EMR_NAME=APP.emr, **DOC_HEADER())


def _docx_header():
    doc = docx.Document()
    doc_header = DOC_HEADER()
    p = doc.add_paragraph(doc_header["PRACTICE_NAME"])  # http://bit.ly/2rAnT4z
    p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("{street}, {city}, {state} {zip}".format(
        street=doc_header["PRACTICE_STREET"],
        city=doc_header["PRACTICE_CITY"],
        state=doc_header["PRACTICE_STATE"],
        zip=doc_header["PRACTICE_ZIP"])
    )
    p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("Tel: {tel} | Fax: {fax}".format(
        tel=doc_header["PRACTICE_NUMBER"],
        fax=doc_header["PRACTICE_FAX"])
    )
    p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
    return doc


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id", "type"]))
def signin_sheet():
    output = StringIO()
    doc = _docx_header()
    h = doc.add_heading("Office Sign-in Sheet", 0)
    h.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
    doc.add_heading("Topic _________________________________            Date ____________", 3)
    doc.add_paragraph()
    p = doc.add_paragraph("Meeting [ %s ]       Training [ %s ]" % (
        "x" if request.get_vars["type"] == "meeting" else " ",
        "x" if request.get_vars["type"] == "training" else " "))
    p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Name'
    hdr_cells[1].text = 'Position'
    hdr_cells[2].text = 'Signature'
    for item in range(10):
        row_cells = table.add_row().cells
        row_cells[0].text = "______________________________"
        row_cells[1].text = "____________________"
        row_cells[2].text = "_____________"
    # doc.add_paragraph()
    # doc.add_heading("Summary:", 3)
    # p = doc.add_paragraph("Duration: ______       Minutes [   ]       Hours [   ]")
    # p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
    # doc.add_paragraph("_______________________________________________________________________________________________")
    # doc.add_paragraph("_______________________________________________________________________________________________")
    # doc.add_paragraph("_______________________________________________________________________________________________")
    # doc.add_paragraph("_______________________________________________________________________________________________")
    # doc.add_paragraph("_______________________________________________________________________________________________")
    doc.save(output)
    response.headers['Content-Type'] = 'application/msword'
    return output.getvalue()


@auth.requires(URL.verify(request, hmac_key=MY_KEY, salt=session.MY_SALT, hash_vars=["app_id"]))
def huddle_sheet():
    output = StringIO()
    doc = _docx_header()
    h = doc.add_heading("Daily Huddle Sheet", 0)
    h.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
    doc.add_heading("Date ____________", 3)
    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Checklist'
    hdr_cells[1].text = 'Huddle Agenda'
    agenda = [
        "Check for patients on the schedule that may require more time/assistance due to age, disability, personal "
        "demeanor, etc. who can help.",
        "Check for back-to-back lengthy appointments, such as physicals. How can they be worked around to prevent "
        "backlog?",
        "Are there openings which can be filled? Chronic now-shows? Any special instructions for the scheduler?",
        "Check over provider and staff schedule - does anyone need to leave early or break for a phone call or "
        "meeting?",
        "Lab results, test results, notes from other physicians, faxes -  are they signed and ready to be scanned "
        "into the patient's chart? Check for outstanding labs, referrals, and diagnostics.",
        "Review current schedule for high risk pts. High risk pts are highlighted in the EMR's OV screen."
    ]
    for item in agenda:
        row_cells = table.add_row().cells
        row_cells[0].text = "[    ]"
        row_cells[1].text = item

    doc.add_heading("Agenda:", 3)
    doc.add_paragraph("_______________________________________________________________________________________________")
    doc.add_paragraph("_______________________________________________________________________________________________")
    doc.add_paragraph("_______________________________________________________________________________________________")

    doc.save(output)
    return output.getvalue()

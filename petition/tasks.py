from textwrap import wrap

from celery import shared_task
from mail_templated import EmailMessage

import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter


@shared_task
def send_signature_verification_email(token, sender, receiver, full_name):
    email = EmailMessage(
        template_name="email/signature_verification.tpl",
        from_email=sender,
        to=[receiver],
        context={
            "token": token,
            "full_name": full_name,
        },
    )
    email.send()


def pdf_generator(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    text_obj = c.beginText()
    text_obj.setTextOrigin(cm, cm)
    text_obj.setFont("Helvetica", 12)
    desc = wrap(data.get("petition_description"), width=40)
    text_obj.textLines(desc)
    c.drawText(text_obj)
    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


@shared_task
def send_successful_petition_report(
    title, owner, recipient_name, recipient_email, report_file_data
):
    email = EmailMessage(
        template_name="email/successful_petition_report.tpl",
        from_email="petition_report@plea.org",
        to=[recipient_email],
        context={"title": title, "owner": owner, "recipient_name": recipient_name},
    )
    pdf = pdf_generator(report_file_data)
    email.attach("petition_report.pdf", pdf, "application/pdf")
    email.send()

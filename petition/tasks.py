from textwrap import wrap

from celery import shared_task
from mail_templated import EmailMessage

import io
import csv


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


def csv_generator(data):
    output_file = io.StringIO()
    cr = csv.writer(output_file, delimiter=",", qouting=csv.QUOTE_ALL)
    cr.writerow(["First_name", "Last_name", "email", "Country"])
    for sgn in data:
        cr.writerow([sgn[0], sgn[1], sgn[2], sgn[3]])
    output_file.getvalue()
    return output_file


@shared_task
def send_successful_petition_report(data):
    email = EmailMessage(
        template_name="email/successful_petition_report.tpl",
        from_email="petition_report@plea.org",
        to=[data.get("petition_recipient_email")],
        context={
            "title": data.get("petition_title"),
            "owner": data.get("petition_owner_name"),
            "recipient_name": data.get("petition_recipient_name"),
        },
    )
    csv_file = csv_generator(data=data.get("petition_signatures"))
    email.attach("report.csv", csv_file.read(), "text/csv")
    email.send()

from celery import shared_task
from mail_templated import EmailMessage


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


@shared_task
def send_successful_petition_report(title, owner, recipient_name, recipient_email):
    email = EmailMessage(
        template_name="email/successful_petition_report.tpl",
        from_email="petition_report@plea.org",
        to=[recipient_email],
        context={
            "title": title,
            "owner": owner,
            "recipient_name": recipient_name
        },
    )
    email.send()

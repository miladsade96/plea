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

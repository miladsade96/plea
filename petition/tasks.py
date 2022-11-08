from celery import shared_task
from mail_templated import EmailMessage


@shared_task
def send_signature_verification_email(token, email, full_name):
    email = EmailMessage(
        template_name="email/signature_verification.tpl",
        from_email="no_reply@plea.org",
        to=[email],
        context={
            "token": token,
            "full_name": full_name,
        },
    )
    email.send()

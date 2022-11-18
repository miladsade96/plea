from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from mail_templated import EmailMessage

from accounts.models import CustomUser


@shared_task
def send_account_activation_email(token, sender, receiver, full_name):
    email = EmailMessage(
        template_name="email/account_activation.tpl",
        from_email=sender,
        to=[receiver],
        context={
            "token": token,
            "full_name": full_name,
        },
    )
    email.send()


@shared_task
def send_password_reset_email(token, sender, receiver, full_name):
    email = EmailMessage(
        template_name="email/password_reset.tpl",
        from_email=sender,
        to=[receiver],
        context={
            "token": token,
            "full_name": full_name,
        },
    )
    email.send()


@shared_task
def clean_up_inactive_user_accounts():
    CustomUser.objects.filter(
        is_active=False, created_at__gt=timezone.now() - timedelta(days=7)
    ).delete()

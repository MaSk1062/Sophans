from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from celery import shared_task

@shared_task
def board_message_email(profile, plain_message, html_context, tenant):
    mail = EmailMultiAlternatives(
        f'New Message From {profile.business}',
        plain_message,
        settings.EMAIL_HOST_USER,
        [tenant.email],
    )
    mail.attach_alternative(html_context, "text/html")
    mail.send()
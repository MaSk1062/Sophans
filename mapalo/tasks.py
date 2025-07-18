from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from .models import *


@shared_task
def send_welcome_email_task(title, welcome_email_context, plain_welcome_email, lord_email):
    welcome_email = EmailMultiAlternatives(
        title,
        plain_welcome_email,
        settings.EMAIL_HOST_USER,
        [lord_email])
    welcome_email.attach_alternative(welcome_email_context, 'text/html')
    welcome_email.send()


@shared_task
def new_user_email_task(notify, notify_body):
    notification = EmailMessage(notify, notify_body, ['stephanmask@gmail.com'])
    notification.fail_silently = False
    notification.send()

@shared_task
def public_email_change_task(email):
    confirmation = EmailMessage(
        'Email Changed',
        'Your email on Sophans has been changed, if this was not you contact +260776514959 or email us @sophans_msn@gmail.com.\n Sophans Team',
        settings.EMAIL_HOST_USER,
        [email]
    )
    confirmation.fail_silently = False
    confirmation.send()

@shared_task
def public_password_change_task(username, email):
    password_email = EmailMessage(
        'Password Changed',
        f'Hello {username}\n Your password has been changed. if you did not do this contact +260776514959 or email us @sophans_msn@gmail.com.\n Sophans Team',
        settings.EMAIL_HOST_USER,
        [email]
    )
    password_email.fail_silently = False
    password_email.send()


@shared_task
def public_account_delete_task(username, email):
    delete_email = EmailMessage(
        'Account Deleted',
        f'Hello {username}\n Your account on Sophans has been deleted.\n Sorry to see you leave us \n Sophans Team',
        settings.EMAIL_HOST_USER,
        [email]
    )
    delete_email.fail_silently = False
    delete_email.send()

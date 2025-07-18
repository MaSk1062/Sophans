from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.conf import settings
from celery import shared_task
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Tenant
import datetime
from django.utils import timezone

from celery import app


@shared_task(name="new tenant email")
def new_tenant_email_task(lord, tenant_context, plain_tenant, tenantemail):
    tenant_email = EmailMultiAlternatives(
        f'Welcome to {lord.business}',
        plain_tenant,
        settings.EMAIL_HOST_USER,
        [tenantemail],
    )
    tenant_email.attach_alternative(tenant_context, 'text/html')
    tenant_email.send()


@shared_task(name="receipt email")
def tenant_receipt_email_task(business, receipt_context, plain_receipt, tenant_mail):
    tenant_receipt = EmailMultiAlternatives(
        f'{business} Receipt.',
        plain_receipt,
        settings.EMAIL_HOST_USER,
        [tenant_mail]
    )
    tenant_receipt.attach_alternative(receipt_context, 'text/html')
    tenant_receipt.send()


#celery beat function
@shared_task(name="email reminder")
def reminder_email_task():
    target_date = timezone.now().date() + datetime.timedelta(days=7)
    tenants = Tenant.objects.filter(due_date=target_date)
    if tenants:
        for tenant in tenants:
            if tenant.user.tenantprofile.has_paid and tenant.boarded:
                reminder_context = render_to_string(
                    'stephan/emails/reminder_email.html', {"tenant": tenant}
                )
                plain_reminder = strip_tags(reminder_context)    
                reminder_email = EmailMultiAlternatives(
                    "Rentals Reminder",
                    plain_reminder,
                    settings.EMAIL_HOST_USER,
                    [tenant.email]
                )
                reminder_email.attach_alternative(reminder_context, 'text/html')
                reminder_email.send()
            else:
                pass


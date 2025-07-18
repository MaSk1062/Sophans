import datetime
from django.template.context_processors import request

from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import BedSpace, BedRoom, Transactions, Tenant, BoardingReceipt
from .utils import get_next_serial
from .tasks import tenant_receipt_email_task
from django.utils.html import strip_tags
from django.template.loader import render_to_string

#Automatic User creation




#automatic max bed space reduction and increment
@receiver(post_save, sender=BedSpace)
def decrement_bedspace(sender, instance, created, **kwargs):
    #Reduce available bed spaces in the Room when a Bedspace is added.
    if created:  # Only when a new Bedspace is created
        instance.bedroom.available_spaces -= 1
        instance.bedroom.save()

@receiver(post_delete, sender=BedSpace)
def increment_bedspace(sender, instance, *args, **kwargs):
    #Increase available bed spaces in the Room when a Bedspace is removed.
    if instance.bedroom:
        instance.bedroom.available_spaces += 1
        instance.bedroom.save()
    else:
        pass


@receiver(post_save, sender=Tenant)
def tenant_bedspace_status(sender, instance, created, **kwargs):
    if created:
        instance.bedspace.occupied = True
        instance.bedspace.save()


@receiver(post_delete, sender=Tenant)
def tenant_bedspace_status(sender, instance, **kwargs):
    if instance.bedspace:
        instance.bedspace.occupied = True
        instance.bedspace.save()


@receiver(pre_save, sender=Tenant)
def boarding_status(sender, instance, *args, **kwargs):
    if instance.pk:
        tenant = Tenant.objects.get(pk=instance.pk)
        if tenant.boarded and instance.boarded == False:
            instance.bedspace.occupied = False
            instance.save()
        elif not tenant.boarded and instance == True:
            instance.bedspace.occupied = True
            instance.save()
        else:
            pass


@receiver(post_save, sender=Tenant)
def tenant_receipt(sender, instance, created, **kwargs):
    lord = instance.user.tenantprofile
    serial = get_next_serial(landlord=instance.user)
    date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    receipt_num = f'Sophans-{lord.business}-{lord.Landlord.id}{lord.id}{date_str}-{serial:03d}'
    if created:
        receipt = BoardingReceipt()
        receipt.landlord = instance.user 
        receipt.tenant = instance
        receipt.receipt_number = receipt_num
        receipt.serial_number = serial
        receipt.amount = instance.amount 
        receipt.due_date = instance.due 
        receipt.save()

        business = lord.business
        receipt_context = render_to_string(
            'stephan/emails/tenant_receipt.html', {'object': receipt}
        )
        plain_receipt = strip_tags(receipt_context)
        tenant_mail = instance.email
        tenant_receipt_email_task.delay(business, receipt_context, plain_receipt, tenant_mail)

@receiver(post_save, sender=Tenant)
def transaction_create(sender, instance, created, *args, **kwargs):
    if created:
        Transactions.objects.create(
            user=instance.user,
            tenant=instance,
            amount=instance.amount
        )


@receiver(pre_save, sender=Tenant)
def create_payment_when_paid(sender, instance, *args, **kwargs):
    # an update, not a new instance
    if instance.pk:  # Ensure it's an update, not a new record
        previous = Tenant.objects.get(pk=instance.pk)
        if previous.paid and instance.paid == False:
            Transactions.objects.create(
                user=instance.user,
                tenant=instance,
                amount=instance.amount,
                paid=False,
            )
        elif not previous.paid and instance.paid:
            Transactions.objects.create(
                user=instance.user,
                tenant=instance,
                amount=instance.amount,
                paid=True,
            )
        else:
            pass


@receiver(post_save, sender=Tenant)
def tenant_update_receipt(sender, instance, *args, **kwargs):
    lord = instance.user.tenantprofile
    serial = get_next_serial(landlord=instance.user)
    date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    receipt_num = f'Sophans-{lord.business}-{lord.Landlord.id}{lord.id}{date_str}-{serial:03d}'
    if instance.pk:
        old_paid = Tenant.objects.get(pk=instance.pk)
        if not old_paid.paid and instance.paid == True:
            receipt = BoardingReceipt()
            receipt.landlord = instance.user
            receipt.tenant = instance
            receipt.receipt_number = receipt_num
            receipt.serial_number = serial
            receipt.amount = instance.amount 
            receipt.due_date = instance.due 
            receipt.save()

            business = lord.business
            receipt_context = render_to_string(
                'stephan/emails/tenant_receipt.html', {'object': receipt}
            )
            plain_receipt = strip_tags(receipt_context)
            tenant_mail = instance.email

            tenant_receipt_email_task.delay(business, receipt_context, plain_receipt, tenant_mail)
        else:
            pass
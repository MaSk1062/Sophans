from typing import Iterable
import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django_resized import ResizedImageField
from django.templatetags.static import static
from django.utils import timezone
from .manager import TenantQuerySet, RoomsQuerySet, BedspaceQuerySet, TransactionQuerySet
from mapalo.models import Client
from datetime import timedelta
from colorfield.fields import ColorField



class TenantProfile(models.Model):
    Landlord = models.OneToOneField(User, on_delete=models.CASCADE)
    business = models.CharField(max_length=100, null=True)
    picture = ResizedImageField(size=[500, 350], upload_to="profile/%Y/%m/%d/", default='images/GT.jpg', null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    contact = models.CharField(max_length=13, null=True, blank=True)
    is_activate = models.BooleanField(default=True, null=True)
    has_paid = models.BooleanField(default=False, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.Landlord}'s Profile"
    

class SiteSetting(models.Model):
    name = models.CharField(max_length=50)
    color = ColorField(default='#5B676D')

    def __str__(self):
        return self.name


class BedRoom(models.Model):
    SEX_CHOICES = {
       "M": "Male",
       "F": "Female",
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    total_spaces = models.PositiveBigIntegerField(default=6)
    available_spaces = models.PositiveIntegerField(default=6, null=True)
    sex = models.CharField(max_length=6, choices=SEX_CHOICES, blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    objects = RoomsQuerySet.as_manager()

    def __str__(self):
        return f'{self.name}-{self.sex}'

    class Meta:
        ordering = ['name']

class BedSpace(models.Model):
    SEX_CHOICES = {
       "M": "Male",
       "F": "Female",
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    bedroom = models.ForeignKey(BedRoom, on_delete=models.SET_NULL, null=True)
    sex = models.CharField(max_length=6, choices=SEX_CHOICES, null=True)
    occupied = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)

    objects = BedspaceQuerySet.as_manager()

    def __str__(self):
        return f"{self.name} in {self.bedroom}"

    def save(self, *args, **kwargs):
        if self.bedroom.available_spaces <= 0:
            raise ValueError("No available spaces in this room.")
        super().save(*args, **kwargs)


    class Meta:
        ordering = ['name']


class Tenant(models.Model):
    SEX_CHOICES = {
       "M": "Male",
       "F": "Female",
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    bedroom = models.ForeignKey(BedRoom, on_delete=models.SET_NULL, null=True)
    bedspace = models.ForeignKey(BedSpace, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, null=True)
    sex = models.CharField(max_length=200, choices=SEX_CHOICES, null=True)
    picture = ResizedImageField(size=[300,300], default="images/Kamado.PNG", upload_to="tenant/%Y/%m/%d/", null=True, blank=True)
    contact = models.CharField(max_length=13, null=True)
    email = models.EmailField(null=True)
    nrc_number = models.CharField(max_length=200, null=True)
    guardians_name = models.CharField(max_length=200, null=True, blank=True)
    guardians_contact = models.CharField(max_length=13, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    school = models.CharField(max_length=200, null=True, blank=True)
    amount = models.CharField(max_length=10, null=True)
    due = models.DateField(null=True)
    notice = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    boarded = models.BooleanField(default=True)
    added = models.DateTimeField(auto_now_add=True)

    objects = TenantQuerySet.as_manager()


    class Meta:
        ordering = ['name']


    def __str__(self):
        return f"{self.name}"
    

class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField(null=True)
    paid = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    objects = TransactionQuerySet.as_manager()


    def __str__(self):
        return f"{self.tenant} Transaction"

    class Meta:
        ordering = ['-date']



class Feedback(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name}"

    class Meta:
        ordering = ['submitted_at']


class BoardingReceipt(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=100, unique=True)
    serial_number = models.PositiveIntegerField()
    amount = models.CharField(max_length=8)
    due_date = models.CharField(max_length=10)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tenant.name} receipt'
    
    class Meta:
        ordering = ['date_created']


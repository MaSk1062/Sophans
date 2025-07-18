from django.conf import settings
from django.db import models
from django_resized import ResizedImageField
from django.contrib.auth.models import User
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    schema_name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, null=True)

    auto_create_schema = True


class Domain(DomainMixin):
    pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100, null=True)
    image = ResizedImageField(size=[500, 350], upload_to="profile/%Y/%m/%d/", default='images/GT.jpg', null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    subdomain = models.CharField(max_length=200, null=True)
    contact = models.CharField(max_length=13, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    is_activate = models.BooleanField(default=True, null=True)
    has_paid = models.BooleanField(default=False, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user}'s Profile"
    

class Review(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name}"

    class Meta:
        ordering = ['submitted_at']


class Blacklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = ResizedImageField(size=[300, 250], upload_to="blacklists/%Y/%m/%d/", default='images/kamado.png')
    reason = models.CharField(max_length=300, null=True)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added']

    def __str__(self):
        return self.name

class SophansImage(models.Model):
    dashboard_image = ResizedImageField(size=[1000, 700], upload_to="sophans_images")
    management_image = ResizedImageField(size=[700, 500], upload_to="sophans_images")
    reminders_image = ResizedImageField(size=[700, 500], upload_to="sophans_images")
    rooms_image = ResizedImageField(size=[700, 500], upload_to="sophans_images")
    payment_image = ResizedImageField(size=[700, 500], upload_to="sophans_images")


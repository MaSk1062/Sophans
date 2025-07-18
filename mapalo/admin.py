from django.contrib import admin
from django_tenants.admin import TenantAdminMixin

from .models import Client, Domain, Profile, Review, Blacklist, SophansImage

@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Domain)
admin.site.register(Profile)
admin.site.register(Review)
admin.site.register(Blacklist)
admin.site.register(SophansImage)




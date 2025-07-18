from django.contrib import admin
from .models import *

admin.site.register(TenantProfile)
admin.site.register(BedRoom)
admin.site.register(BedSpace)
admin.site.register(Tenant)
admin.site.register(Transactions)
admin.site.register(Feedback)
admin.site.register(BoardingReceipt)
admin.site.register(SiteSetting)
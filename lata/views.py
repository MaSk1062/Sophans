import threading
from email.message import EmailMessage

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import MessageForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from stephan.models import Tenant, TenantProfile
import os
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .tasks import board_message_email


@login_required()
def messages(request):
    reminders = Message.objects.filter(author=request.user)
    profile = TenantProfile.objects.get(Landlord=request.user)
    tenants = Tenant.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            notify = form.save(commit=False)
            notify.author = request.user
            notify.save()

            html_context = render_to_string(
                'lata/dm_email.html', context={'body': notify.body, 'business_name': profile.business}
            )
            plain_message = strip_tags(html_context)

            for tenant in tenants:
                if tenant.boarded:
                    board_message_email.delay(profile, plain_message, html_context, tenant)
                else:
                    pass

            return redirect('lata')
    else:
        form = MessageForm()

    context = {
        'tenants': tenants,
        'reminders': reminders,
        'form': form,
    }
    return render(request, 'lata/home.html', context)



def messages_email(request):
    return render(request, 'lata/messages_email.html')



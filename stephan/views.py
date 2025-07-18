import datetime
import xlwt
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import *
from .filters import TenantFilter, BedroomFilter, BedspaceFilter, TransactionFilter, ReceiptFilter
from .forms import TenantForm, EmailChangeForm, BedspaceForm, ProfileUpdateForm, SignUpForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.core.mail import EmailMessage
from lata.models import Message
from .tasks import *
import functools
#from weasyprint import HTML
#import tempfile
from django_ratelimit.decorators import ratelimit
from .utils import get_next_serial
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives



def msg(request):
    return render(request, 'stephan/emails/tenant_email.html')


def receipt(request):
    return render(request, 'stephan/emails/tenant_receipt.html')


def welcome(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('tenant-signup')


def signup(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            landlord = form.save(commit=False)
            landlord.save()

            TenantProfile.objects.create(
                Landlord = landlord,
                business = landlord.username,
            )

            landlord = authenticate(request, username=landlord.username, password=request.POST['password1'])

            if landlord is not None:
                login(request, landlord)
                return redirect('sophans')
            return redirect('sophans')
    else:
        form = SignUpForm()

    context = {
        'form': form,
    }
    return render(request, 'stephan/auth/signup.html', context)



@login_required(login_url='tenant-login')
def landlordLogout(request):
    logout(request)
    return redirect('welcome')




"""@ratelimit(key="ip", rate="10/h")
def landlordLogin(request):
    page = "login"
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

    return render(request, 'stephan/login.html', {"page":page})"""



@login_required(login_url='tenant-login')
def home(request):
    tenant = Tenant.objects.filter(user=request.user).select_related('bedspace', 'bedroom')
    room = BedRoom.objects.filter(user=request.user)
    space = BedSpace.objects.filter(user=request.user)
    males = Tenant.objects.get_males()
    females = Tenant.objects.get_females()
    mrooms = BedRoom.objects.for_males()
    frooms = BedRoom.objects.for_females()
    bmales = BedSpace.objects.for_males()
    bfemales = BedSpace.objects.for_females()

    #tenant pagination
    t_paginator = Paginator(tenant, settings.PAGE_SIZE)
    t_page_number = request.GET.get('page', 1)
    tenant_page = t_paginator.get_page(t_page_number)

    #room pagination
    r_paginator = Paginator(room, settings.PAGE_SIZE)
    r_page_number = request.GET.get('page', 1)
    room_page = r_paginator.get_page(r_page_number)

    #bedspace pagination
    b_paginator = Paginator(space, settings.PAGE_SIZE)
    b_page_number = request.GET.get('page', 1)
    space_page = b_paginator.get_page(b_page_number)
    context = {
        'tenant_page': tenant_page,
        'rooms_page': room_page,
        'space_page': space_page,
        'tenants':tenant,
        'rooms':room,
        'spaces':space,
        'males': males,
        'females': females,
        'mrooms': mrooms,
        'frooms': frooms,
        'bmales': bmales,
        'bfemales': bfemales,
    }
    return render(request, 'stephan/home.html', context)





@login_required(login_url='tenant-login')
def profileUpdate(request):
    form = ProfileUpdateForm(instance=request.user.tenantprofile)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.tenantprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user.tenantprofile)
    return render(request, 'stephan/partials/profile_update.html', {'form': form})

@login_required(login_url='tenant-login')
def profileview(request):
    profile = TenantProfile.objects.filter(Landlord=request.user)
    return render(request, 'stephan/profile.html', {'profile': profile})


@login_required(login_url='tenant-login')
def roomList(request):
    room = BedroomFilter(request.GET, queryset=BedRoom.objects.filter(user=request.user))
    male_rooms = room.qs.for_males()
    female_rooms = room.qs.for_females()
    total_rooms = male_rooms + female_rooms
    available_rooms = room.qs.available_rooms()

    paginator = Paginator(room.qs, settings.PAGE_SIZE)
    page_num = request.GET.get('page', 1)
    room_page = paginator.get_page(page_num)

    context = {
        'room_page': room_page,
        'rooms': room,
        'male_rooms': male_rooms,
        'female_rooms': female_rooms,
        'total': total_rooms,
        'available': available_rooms
    }
    return render(request, 'stephan/rooms.html', context)

@login_required(login_url='tenant-login')
def bedspaceList(request):
    space = BedspaceFilter(request.GET, queryset=BedSpace.objects.filter(user=request.user))
    male = space.qs.for_males()
    females = space.qs.for_females()

    paginator = Paginator(space.qs, settings.PAGE_SIZE)
    page_nmb = request.GET.get('page', 1)
    space_page = paginator.get_page(page_nmb)

    context = {
        'space_page': space_page,
        'spaces': space,
        'males': male,
        'females': females,
    }
    return render(request, 'stephan/bedspaces.html', context)

@login_required(login_url='tenant-login')
def tenantList(request):
    tenants = TenantFilter(request.GET, queryset=Tenant.objects.filter(user=request.user).select_related('bedspace', 'bedroom'))
    total_males = tenants.qs.get_males()
    total_females = tenants.qs.get_females()
    total_tenants = total_males + total_females

    paginator = Paginator(tenants.qs, settings.PAGE_SIZE)
    page_no = request.GET.get('page', 1)
    tenants_page = paginator.get_page(page_no)
    context = {
        "tenants_page": tenants_page,
        "tenants": tenants,
        "males":total_males,
        "females":total_females,
        "total_tenants": total_tenants,
    }
    return render(request, 'stephan/tenant.html', context )


class TenantUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Tenant
    fields = ['name', 'sex', 'picture', 'contact', 'email',
              'nrc_number', 'guardians_name', 'guardians_contact', 'location',
              'school', 'amount', 'due', 'paid', 'boarded'
              ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        tenant = self.get_object()
        if self.request.user == tenant.user:
            return True
        return False
    
    
    def get_success_url(self):
        return reverse_lazy("tenant-detail", kwargs={'pk': self.kwargs['pk']})

@login_required(login_url='tenant-login')
def tenantcreate(request):
    form = TenantForm()
    lord = TenantProfile.objects.get(Landlord=request.user)
    landlord = request.user
    receipt = BoardingReceipt()
    if request.method == 'POST':
        form = TenantForm(request.POST, request.FILES)
        if form.is_valid():
            ten_form = form.save(commit=False)
            ten_form.user = request.user
            ten_form.save()

            serial = get_next_serial(landlord)

            date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            r_num = f'Sophans-{lord.business}-{lord.Landlord.id}{lord.id}{date_str}-{serial:03d}'
            #receipt_number format = Sophans-{profile.business_name}-{user_id}{profile_id}{datetime}-{serial_number}
            receipt.landlord = request.user 
            receipt.tenant = ten_form
            receipt.receipt_number = r_num
            receipt.serial_number = serial
            receipt.amount = ten_form.amount 
            receipt.due_date = ten_form.due 
            receipt.save()

            #tenant email
            tenantemail = ten_form.email
            tenant_context = render_to_string(
                'stephan/emails/tenant_email.html', {'tenant': ten_form, 'lord': lord}
            )
            plain_tenant = strip_tags(tenant_context)

            new_tenant_email_task.delay(lord, tenant_context, plain_tenant, tenantemail)

            #tenant receipt
            receipt_context = render_to_string(
                'stephan/emails/tenant_receipt.html', context={'object': receipt}
            )
            plain_receipt = strip_tags(receipt_context)
            
            business = lord.business
            tenant_mail = ten_form.email
            
            tenant_receipt_email_task.delay(business, receipt_context, plain_receipt, tenant_mail)
            
            return redirect("tenants")
    else:
        form = TenantForm()
    context = {
        "form": form,
    }
    return render(request, 'stephan/tenant_form.html', context)

class TenantDetailView(LoginRequiredMixin, DetailView):
    model = Tenant
    template_name = 'stephan/tenant_detail.html'
    context_object_name = 'tenant'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = Transactions.objects.filter(tenant=self.object)
        return context

class TenantDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tenant
    success_url = reverse_lazy("tenants")

    def test_func(self):
        tenant = self.get_object()
        if self.request.user == tenant.user:
            return True
        return False

class BedroomCreateView(LoginRequiredMixin, CreateView):
    model = BedRoom
    fields = ["name", "total_spaces", "available_spaces", "sex"]
    success_url = reverse_lazy("rooms")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)



class BedroomDetailView(LoginRequiredMixin, DetailView):
    model = BedRoom
    template_name = "stephan/bedroom_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bedspaces'] = BedSpace.objects.filter(bedroom=self.object)
        context['tenants'] = Tenant.objects.filter(bedroom=self.object).select_related('bedspace')
        return context
    
class BedroomUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BedRoom
    fields = ["name", "total_spaces", "available_spaces", "sex"]
    template_name = 'stephan/bedroom_update_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        bedroom = self.get_object()
        if self.request.user == bedroom.user:
            return True
        return False

    def get_success_url(self):
        return reverse_lazy("bedroom-detail", kwargs={'pk': self.kwargs['pk']})
    

class BedroomDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BedRoom
    success_url = reverse_lazy("rooms")

    def test_func(self):
        bedroom = self.get_object()
        if self.request.user == bedroom.user:
            return True
        return False
    

class BedspaceCreateView(LoginRequiredMixin, CreateView):
    model = BedSpace
    template_name = 'stephan/bedspace_form.html'
    fields = ["name", "bedroom", "sex"]
    success_url = reverse_lazy("bedspaces")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class BedspaceDetailView(LoginRequiredMixin, DetailView):
    model = BedSpace
    template_name = "stephan/bedspace_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenants'] = Tenant.objects.filter(bedspace=self.object).select_related('bedspace', 'bedroom')
        return context

class BedspaceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BedSpace
    template_name = 'stephan/bedspace_update_form.html'
    fields = ["name", "bedroom", "occupied"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        bedspace = self.get_object()
        if self.request.user == bedspace.user:
            return True
        return False

    def get_success_url(self):
        return reverse_lazy("bedspace-detail", kwargs={'pk': self.kwargs['pk']})
    

class BedspaceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BedSpace
    success_url = reverse_lazy("bedspaces")

    def test_func(self):
        bedroom = self.get_object()
        if self.request.user == bedroom.user:
            return True
        return False



class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'stephan/settings.html'


@login_required(login_url='tenant-login')
def change_email(request):
    form = EmailChangeForm()
    if request.method == "POST":
        form = EmailChangeForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.email = form.cleaned_data["new_email"]
            request.user.save()
            messages.success(request, "Your email has been successfully updated.")
            return redirect("settings")  # Or wherever you want
    else:
        form = EmailChangeForm(user=request.user)
    return render(request, 'stephan/email_change.html', {'form': form})

@login_required(login_url='tenant-login')
def deleteUserData(request):
    if request.method == "POST":
        password = request.POST.get("password")

        if not request.user.check_password(password):
            messages.error(request, "Incorrect password. Please try again.")
            return redirect("delete-user-data")

        rooms = BedRoom.objects.filter(user=request.user)
        if rooms:
            rooms.delete()
        else:
            pass


        spaces = BedSpace.objects.filter(user=request.user)
        if spaces:
            spaces.delete()
        else:
            pass


        notif = Message.objects.filter(author=request.user)
        if notif:
            notif.delete()
        else:
            pass


        payments = Transactions.objects.filter(user=request.user)
        if payments:
            payments.delete()
        else:
            pass

        tenants = Tenant.objects.filter(user=request.user)
        if tenants:
            tenants.delete()
        else:
            pass

        return redirect('home')

    return render(request, 'stephan/data_delete.html')

@login_required(login_url='tenant-login')
def deleteAccount(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirmation_text = request.POST.get("confirmation_text")

        # Ensure user typed "DELETE" to confirm
        if confirmation_text != "DELETE":
            messages.error(request, "You must type 'DELETE' to confirm.")
            return redirect("delete-user-data")

        # Verify password before deletion
        if not request.user.check_password(password):
            messages.error(request, "Incorrect password. Please try again.")
            return redirect("delete-user-data")

        email = EmailMessage(
            f'Account Deleted',
            f'Hello {request.user}, You account has been Scheduled for Deletion.'
            f'But you can still login with a week from today to cancel the deletion process.'
            f'Sorry to see you leave.\n'
            f'Stephan Nguso.',
            settings.EMAIL_HOST_USER,
            [request.user.email],
        )
        email.fail_silently = False
        email.send()


        # Delete the user account
        profile = TenantProfile.objects.filter(user=request.user)
        profile.is_activate = False

        # Log the user out and redirect to homepage
        logout(request)
        messages.success(request, "Your account has been Scheduled for Deletion.")
        return redirect("http://127.0.0.1:8000/")  # Redirect to your public home page

    return render(request, 'stephan/delete_account.html')

@login_required(login_url='tenant-login')
def aboutMnsft(request):
    return render(request, 'stephan/about_us.html')


@login_required(login_url='tenant-login')
def transactionsList(request):
    transactions = TransactionFilter(request.GET, queryset=Transactions.objects.filter(user=request.user))

    paid_total = transactions.qs.paid_total()
    unpaid_total = transactions.qs.unpaid_total()

    total = paid_total + unpaid_total

    paginator = Paginator(transactions.qs, settings.PAGE_SIZE)
    page_number = request.GET.get('page', 1)
    transactions_page = paginator.get_page(page_number)
    context = {
        'transactions_page': transactions_page,
        'transactions': transactions,
        'paid_total': paid_total,
        'unpaid_total': unpaid_total,
        'total': total,
    }
    return render(request, 'stephan/transactions.html', context)


def submit_feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            Feedback.objects.create(name=name, email=email, message=message)
            messages.success(request, "Thank you for your feedback!")

            email = EmailMessage(
                f'Feedback from {name}',
                f'{email}\n'
                f'{message}',
                settings.EMAIL_HOST_USER,
                ['stephanmask@gmail.com'],
            )
            email.fail_silently = False
            email.send()

        else:
            messages.error(request, "Please fill in all fields.")

        return redirect("about-us")
    return render(request, 'stephan/about_us.html')

@login_required(login_url='tenant-login')
def term_privacy(request):
    #return redirect("signup")
    return render(request, 'stephan/partials/terms.html')

"""
@login_required(login_url='tenant-login')
def tenant_pdf(request):
    landlord = request.user
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{landlord.profile.business_name}_Tenants_List_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf"'
    response['Content-Transfer-Encoding'] = 'binary'


    tenants = Tenant.objects.filter(user=landlord)
    total_tenants = tenants.count()

    html_string = render_to_string('stephan/docs/tenant_pdf.html', {'landlord': landlord,'tenants': tenants, 'total_tenants': total_tenants})
    html = HTML(string=html_string)

    # Generate the PDF and write directly to response
    pdf_bytes = html.write_pdf()
    response.write(pdf_bytes)

    return response


@login_required(login_url='tenant-login')
def transactions_pdf(request):
    landlord = request.user
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = f'inline; filename="{landlord.profile.business_name}_Tenant_Payments{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf"'
    response['Content-Transfer-Encoding'] = 'binary'

    transactions = Transactions.objects.filter(user=landlord)
    total_transactions = transactions.count()

    html_string = render_to_string('stephan/docs/transactions_pdf.html',
                                   {'landlord': landlord, 'transactions': transactions, 'total_transactions': total_transactions})
    html = HTML(string=html_string)

    # Generate the PDF and write directly to response
    pdf_bytes = html.write_pdf()
    response.write(pdf_bytes)

    return response

@login_required(login_url='tenant-login')
def tenant_excel(request):
    landlord = request.user
    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = f'inline; filename="{landlord.profile.business_name}_Tenants{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Tenants')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Name', 'Sex', 'Contact', 'Amount', 'Space', 'Added']

    for col in range(len(columns)):
        ws.write(row_num, col, columns[col], font_style)

    font_style = xlwt.XFStyle()

    rows = Tenant.objects.filter(user=landlord).values_list('name', 'sex', 'contact', 'amount', 'bedspace', 'added')

    for row in rows:
        row_num +=1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)

    return response


@login_required(login_url='tenant-login')
def transactions_excel(request):
    landlord = request.user
    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = f'inline; filename="{landlord.profile.business_name}_Tenant_Payments{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Payments')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Name', 'Amount', 'Paid', 'Date']

    for col in range(len(columns)):
        ws.write(row_num, col, columns[col], font_style)

    font_style = xlwt.XFStyle()

    rows = Transactions.objects.filter(user=landlord).values_list('tenant', 'amount', 'paid', 'date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)

    return response"""


@login_required(login_url='tenant-login')
def my_receipts(request):
    receipts = ReceiptFilter(request.GET, queryset=BoardingReceipt.objects.filter(landlord=request.user))

    paginator = Paginator(receipts.qs, settings.PAGE_SIZE)
    page_number = request.GET.get('page', 1)
    receipts_page = paginator.get_page(page_number)
    context = {
        'my_receipts': receipts,
        'receipt_page': receipts_page,

    }
    return render(request, 'stephan/my_receipts.html', context)


class ReceiptDetailView(LoginRequiredMixin, DetailView):
    model = BoardingReceipt
    template_name = 'stephan/receipts_detail.html'

    
"""
@login_required(login_url='tenant-login')
def receipts_pdf(request):
    lord = request.user
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = f'inline; filename="{lord.tenantprofile.business}_Tenant_receipts{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf"'
    response['Content-Transfer-Encoding'] = 'binary'

    receipts = BoardingReceipt.objects.filter(landlord=lord)
    total_receipts = receipts.count()

    html_string = render_to_string('stephan/docs/receipts_pdf.html',
                                   {'landlord': lord, 'receipts': receipts, 'total_receipts': total_receipts})
    html = HTML(string=html_string)

    # Generate the PDF and write directly to response
    pdf_bytes = html.write_pdf()
    response.write(pdf_bytes)

    return response"""
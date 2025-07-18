import threading
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import LandlordRegForm, ProfileUpdateForm, ChangeEmailForm, BlacklistForm
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django_ratelimit.decorators import ratelimit
from django.core.mail import EmailMessage
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import *
from payment.models import Plan, Subscriptions, MyPlan
import datetime
from.tasks import *
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from email.message import EmailMessage


def home(request):
    if request.user.is_authenticated:
        user_email = request.user.email
        if Subscriptions.objects.filter(payer_email=user_email).exists():
            plans = MyPlan.objects.all()
            sophans_images = SophansImage.objects.all()
            return render(request, 'mapalo/home.html', {'plans': plans, 'sophans_images': sophans_images})
        else:
            plans = Plan.objects.all()
            sophans_images = SophansImage.objects.all()
            return render(request, 'mapalo/home.html', {'plans': plans, 'sophans_images': sophans_images})
    else:
        plans = Plan.objects.all()
        sophans_images = SophansImage.objects.all()
        return render(request, 'mapalo/home.html', {'plans': plans, 'sophans_images': sophans_images})


#rate limiting here
def signup(request):
    form = LandlordRegForm()
    if request.method == 'POST':
        form = LandlordRegForm(request.POST)
        if form.is_valid():
            landlord = form.save(commit=False)
            landlord.save()

            lord_username = landlord.username
            lord_first_name = landlord.first_name
            lord_last_name = landlord.last_name
            lord_email = landlord.email

            Profile.objects.create(
                user=landlord,
                business_name=landlord.username,
                subdomain=f'{landlord.username}.{settings.BASE_URL}'
            )

            tenant = Client()
            tenant.name = lord_username
            tenant.schema_name = lord_username
            tenant.save()
            
            domain = Domain()
            domain.domain = f"{lord_username}.{settings.BASE_URL}"
            domain.tenant = tenant
            domain.is_primary = True
            domain.save()


            welcome_email_context = render_to_string('mapalo/partials/welcome_email.html', {'user': landlord.username})
            plain_welcome_email = strip_tags(welcome_email_context)

            title = "Welcome to Sophans"
            send_welcome_email_task.delay(title, welcome_email_context, plain_welcome_email, lord_email)
            
            landlord = authenticate(request, username=landlord.username, password=request.POST['password1'])


            notify = "New User registered",
            notify_body = f'Name: {lord_username}.\n {lord_first_name} {lord_last_name}',

            new_user_email_task.delay(notify, notify_body)

            if landlord is not None:
                login(request, landlord)
                return redirect('signup-terms')
            return redirect('signup-terms')
    else:
        form = LandlordRegForm()

    context = {
        'form': form,
    }
    return render(request, 'mapalo/auth/signup.html', context)

def welcome_email(request):
    return render(request, 'mapalo/partials/welcome_email.html')


@ratelimit(key="ip", rate="10/h")
def landlordLogin(request):
    page = "login"
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('sophans')

    return render(request, 'mapalo/auth/login.html', {"page":page})


@login_required(login_url='public-login')
def landlordLogout(request):
    logout(request)
    return redirect('sophans')


@login_required(login_url='public-login')
def profileFinish(request):
    form = ProfileUpdateForm(instance=request.user.profile)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()

            my_plan_id = request.session.get('my_plan')
            if my_plan_id:
                return redirect('plan-details', plan_id=my_plan_id)
            else:
                return redirect('public-profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'mapalo/profile_onboarding.html', {'form': form})


@login_required(login_url='public-login')
def profileEdit(request):
    form = ProfileUpdateForm(instance=request.user.profile)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('public-profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'mapalo/profile_update.html', {'form': form})

@login_required(login_url='public-login')
def profileview(request):
    profile = Profile.objects.filter(user=request.user)
    return render(request, 'mapalo/public-profile.html', {'profile': profile})

@login_required(login_url='public-login')
def subDomainRedirect(request):
    me = request.user.username
    return redirect(f'http://{me}.{settings.BASE_URL}/')


def features(request):
    return render(request, 'mapalo/features.html')



def about(request):
    return render(request, 'mapalo/about_us.html')



def terms(request):
    return render(request, 'mapalo/terms.html')


@login_required(login_url='public-login')
def signupTerms(request):
    return render(request, 'mapalo/signup-terms.html')


@login_required(login_url='public-login')
def termsAggreement(request):
    return redirect('profile-finish')


def submit_feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            Review.objects.create(name=name, email=email, message=message)
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

        return redirect("about-sophans")
    return render(request, 'mapalo/about_us.html')

@login_required(login_url='public-login')
def feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            Review.objects.create(name=name, email=email, message=message)
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

        return redirect("feedback-send")
    return render(request, 'mapalo/feedback-form.html')


@login_required(login_url='public-login')
def publicSettings(request):
    return render(request, 'mapalo/public-settings.html')


@login_required(login_url='public-login')
def emailChange(request):
    form = ChangeEmailForm()
    if request.method == "POST":
        form = ChangeEmailForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.email = form.cleaned_data["new_email"]
            request.user.save()
            messages.success(request, "Your email has been successfully updated.")

            email = request.user.email
            public_email_change_task.delay(email)

            return redirect('public-settings')
    else:
        form = ChangeEmailForm()
    return render(request, 'mapalo/partials/public_email_change.html', {'form': form})

@login_required()
def accountDelete(request):
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
            return redirect("account-delete")
        
        username = request.user.username
        email = request.user.email

        public_account_delete_task.delay(username, email)


        # Delete the user account
        profile = Profile.objects.filter(user=request.user)
        profile.is_activate = False

        # Log the user out and redirect to homepage
        logout(request)
        messages.success(request, "Your account has been Scheduled for Deletion.")
        return redirect("http://127.0.0.1:8000/")  # Redirect to your public home page

    return render(request, 'mapalo/partials/account_delete.html')

@login_required(login_url='public-login')
def blacklist_tenant(request):
    blacklist_form = BlacklistForm()

    if request.method == "POST":
        blacklist_form = BlacklistForm(request.POST, request.FILES)
        if blacklist_form.is_valid():
            black_list = blacklist_form.save(commit=False)
            black_list.user = request.user
            black_list.save()

            return redirect('blacklists')
    else:
        blacklist_form = BlacklistForm()

    return render(request, 'mapalo/blacklist_form.html', context={'blacklist_form': blacklist_form})


class BlacklistListView(LoginRequiredMixin, ListView):
    model = Blacklist
    template_name = 'mapalo/blacklists.html'
    context_object_name = 'blacklists'


class BlacklistUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Blacklist
    template_name = 'mapalo/blacklist_update.html'
    fields = ['name', 'image', 'reason']
    success_url = reverse_lazy('blacklists')


    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        blacklist = self.get_object()
        if self.request.user == blacklist.user:
            return True
        return False
    
class BlacklistDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = Blacklist
    template_name = 'mapalo/blacklist_delete.html'
    success_url = reverse_lazy('blacklists')


    def test_func(self):
        blacklist = self.get_object()
        if self.request.user == blacklist.user:
            return True
        return False

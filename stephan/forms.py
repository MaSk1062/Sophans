from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Tenant, BedSpace, TenantProfile
import re





class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({"class": "form-control", 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({"class": "form-control", 'placeholder': 'Last Name'})
        self.fields['username'].widget.attrs.update({"class": "form-control", 'placeholder': 'Business Name'})
        self.fields['email'].widget.attrs.update({"class": "form-control", 'placeholder': 'Email Address'})
        self.fields['password1'].widget.attrs.update({"class": "form-control", 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({"class": "form-control", 'placeholder': 'Confirm Password'})


class TenantForm(ModelForm):
    class Meta:
        model = Tenant
        fields = ["bedroom", "bedspace", "name", "sex", "picture", "contact", "email", "location",
                  "nrc_number", "guardians_name", "guardians_contact", "school", "amount",
                  "due", "paid", 'boarded']
        widgets = {
            'due': forms.widgets.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(TenantForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({"class": "form-control", 'placeholder': 'Name..'})
        self.fields['sex'].widget.attrs.update({"class": "form-control", 'placeholder': 'Male or Female'})
        self.fields['picture'].widget.attrs.update({"class": "form-control", 'placeholder': 'Photo'})
        self.fields['contact'].widget.attrs.update({"class": "form-control", 'placeholder': 'Contact...'})
        self.fields['email'].widget.attrs.update({"class": "form-control", 'placeholder': 'Email...'})
        self.fields['location'].widget.attrs.update({"class": "form-control", 'placeholder': 'From(Location)'})
        self.fields['nrc_number'].widget.attrs.update({"class": "form-control", 'placeholder': 'Registration No..'})
        self.fields['guardians_name'].widget.attrs.update({"class": "form-control", 'placeholder': 'Guardians Name'})
        self.fields['guardians_contact'].widget.attrs.update({"class": "form-control", 'placeholder': 'Guardians Contact'})
        self.fields['school'].widget.attrs.update({"class": "form-control", 'placeholder': 'School'})
        self.fields['amount'].widget.attrs.update({"class": "form-control", 'placeholder': 'Amount Paid'})
        self.fields['due'].widget.attrs.update({"class": "form-control", 'placeholder': 'Due Date'})

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')

        # Ensure the contact is exactly 13 characters long
        if not contact or len(contact) != 13:
            raise forms.ValidationError("Contact number must be exactly 13 characters long.")

        # Ensure it starts with a valid country code format (e.g., +260, +254, etc.)
        if not re.match(r"^\+\d{12}$", contact):
            raise forms.ValidationError("Invalid contact format. It must start with '+260' ")

        if Tenant.objects.filter(contact=contact).exists():
            raise forms.ValidationError("Contact Already Belongs To Another Tenant")

        return contact

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Tenant.objects.filter(email=email).exists():
            raise forms.ValidationError("Email Already In Use")
        return email




class EmailChangeForm(forms.Form):
    new_email = forms.EmailField(label="New Email")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_new_email(self):
        email = self.cleaned_data.get("new_email")
        if self.user.email == email:
            raise forms.ValidationError("This is already your current email.")
        from django.contrib.auth import get_user_model
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class BedspaceForm(forms.ModelForm):
    class Meta:
        model = BedSpace
        fields = ['name', 'bedroom', 'sex']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = TenantProfile
        fields = ["business", "picture", "location", "address", "contact"]
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client, Profile, Blacklist


class LandlordRegForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(LandlordRegForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({"class": "form-control", 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({"class": "form-control", 'placeholder': 'Last Name'})
        self.fields['username'].widget.attrs.update({"class": "form-control", 'placeholder': 'Business Name'})
        self.fields['email'].widget.attrs.update({"class": "form-control", 'placeholder': 'Email Address'})
        self.fields['password1'].widget.attrs.update({"class": "form-control", 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({"class": "form-control", 'placeholder': 'Confirm Password'})

class TenantForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'schema_name']
        widgets = {
            'name' : forms.TextInput(attrs={'placeholder': 'Name...'}),
            'schema_name' : forms.TextInput(attrs={'placeholder': 'Business Name'}),
        } 
        
    def clean_schema_name(self):
        schema_name = self.cleaned_data['schema_name'].lower() 

        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', schema_name):
            raise forms.ValidationError("Business names can only contain lowercase letters, numbers, and hyphens!")
        
        if Client.objects.filter(schema_name=schema_name).exists():
            raise forms.ValidationError("This nickname is already taken, Check Registration Email for the link to your Business Site")
        
        return schema_name


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["user", "is_activate", "has_paid"]
        widgets = {
            'image' : forms.FileInput(),
            'address': forms.TextInput(attrs={'placeholder': 'Enter Address...'}),
            'location' : forms.TextInput(attrs={'placeholder': 'Add Location...'}),
        }


class ChangeEmailForm(forms.Form):
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


class BlacklistForm(forms.ModelForm):
    class Meta:
        model = Blacklist
        fields = ['name', 'image', 'reason']
        widgets = {
            'image': forms.FileInput(),
            'name': forms.TextInput(attrs={'placeholder': 'Fullname'}),
            'reason': forms.TextInput(attrs={'placeholder': 'Reason for blacklisting'})
        }


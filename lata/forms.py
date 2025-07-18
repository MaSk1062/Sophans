from django.forms import ModelForm
from django import forms
from .models import Message

class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.TextInput(attrs={'class':'form-control','placeholder': 'Send Message to Tenants...'})
        }
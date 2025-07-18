from django.urls import path
from lata import views

urlpatterns = [
    path('', views.messages, name='lata'),
    path('email-template/', views.messages_email, name='email'),
]
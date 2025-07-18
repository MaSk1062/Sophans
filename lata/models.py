from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from stephan.models import Tenant



class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    body = models.CharField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created']


    def __str__(self):
        return f'{self.author.username} message board'

from django.contrib import admin
from .models import Client, Mailing, Message

# Register your models here.
admin.site.register(Client)
admin.site.register(Mailing)
admin.site.register(Message)

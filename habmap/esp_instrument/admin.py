from django.contrib import admin
from .models import EspInstrument, Deployment

# Register your models here.

admin.site.register(EspInstrument)

admin.site.register(Deployment)

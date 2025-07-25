# juegos/admin.py
from django.contrib import admin
from .models import RondaBolirana, DetalleRonda

admin.site.register(RondaBolirana)
admin.site.register(DetalleRonda)
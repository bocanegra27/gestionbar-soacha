# reportes/admin.py
from django.contrib import admin
from .models import CierreCaja

@admin.register(CierreCaja)
class CierreCajaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'responsable', 'total_ventas_sistema', 'total_efectivo_contado', 'diferencia')
    list_filter = ('fecha', 'responsable')
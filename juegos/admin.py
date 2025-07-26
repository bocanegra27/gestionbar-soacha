# juegos/admin.py
from django.contrib import admin
from .models import RondaBolirana, DetalleRonda
from django.utils import timezone # <-- Importamos timezone

# --- CAMBIO 1: Creamos una clase de admin personalizada para RondaBolirana ---
@admin.register(RondaBolirana)
class RondaBoliranaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'nombre_perdedor', 'hora_inicio', 'hora_pago', 'estado')
    list_filter = ('estado', 'fecha_creacion')

    def hora_inicio(self, obj):
        local_time = timezone.localtime(obj.fecha_creacion)
        return local_time.strftime("%d/%m/%Y %I:%M %p")
    hora_inicio.short_description = 'Hora Inicio'

    def hora_pago(self, obj):
        if obj.fecha_pago:
            local_time = timezone.localtime(obj.fecha_pago)
            return local_time.strftime("%d/%m/%Y %I:%M %p")
        return "---"
    hora_pago.short_description = 'Hora Pago'

# Dejamos el registro simple para DetalleRonda, ya que no necesitamos personalizarlo
admin.site.register(DetalleRonda)
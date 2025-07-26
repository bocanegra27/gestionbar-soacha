# ventas/admin.py
from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from .models import Pedido, DetallePedido, Mesa
from django.utils import timezone

admin.site.register(Mesa)

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    autocomplete_fields = ['producto']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # --- CAMBIO 1: Añadimos la nueva columna 'hora_facturacion' ---
    list_display = ('id', 'mesa', 'hora_apertura', 'hora_facturacion', 'estado', 'total_formateado')
    list_filter = ('estado', 'fecha_hora', 'mesa')
    inlines = [DetallePedidoInline]
    
    # Renombramos la función para mayor claridad
    def hora_apertura(self, obj):
        local_time = timezone.localtime(obj.fecha_hora)
        return local_time.strftime("%d/%m/%Y %I:%M %p")
    
    hora_apertura.short_description = 'Hora Apertura'

    # --- CAMBIO 2: Añadimos la nueva función para formatear la hora de facturación ---
    def hora_facturacion(self, obj):
        # Comprobamos si el pedido ya ha sido facturado
        if obj.fecha_facturacion:
            local_time = timezone.localtime(obj.fecha_facturacion)
            return local_time.strftime("%d/%m/%Y %I:%M %p")
        # Si no, mostramos un guion
        return "---"
    
    hora_facturacion.short_description = 'Hora Facturación'

    def total_formateado(self, obj):
        return f"${intcomma(int(obj.total))}"
    
    total_formateado.short_description = 'Total'
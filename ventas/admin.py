# ventas/admin.py
from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from .models import Pedido, DetallePedido, Mesa

# 1. Registramos el modelo Mesa para poder gestionarlo en el admin
admin.site.register(Mesa)

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    autocomplete_fields = ['producto']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # 2. Usamos 'total_formateado' en lugar de 'total'
    list_display = ('id', 'mesa', 'fecha_hora', 'estado', 'total_formateado')
    list_filter = ('estado', 'fecha_hora', 'mesa')
    inlines = [DetallePedidoInline]
    
    # También añadimos 'mesa' a la lista para verla de un vistazo

    def total_formateado(self, obj):
        return f"${intcomma(int(obj.total))}"
    
    total_formateado.short_description = 'Total'
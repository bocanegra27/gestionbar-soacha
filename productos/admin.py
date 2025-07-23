# productos/admin.py
from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from .models import Categoria, Producto # Importamos Categoria y Producto desde models.py de la misma carpeta (.)

# Register your models here.
admin.site.register(Categoria)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'disponible')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre', 'categoria__nombre') # Habilita la búsqueda

# 1. Creamos una función para formatear el precio
    def precio_formateado(self, obj):
        # Primero convertimos a entero para quitar decimales, luego aplicamos intcomma
        return f"${intcomma(int(obj.precio))}"
    
    # 2. Le damos un nombre a la columna en el admin
    precio_formateado.short_description = 'Precio'
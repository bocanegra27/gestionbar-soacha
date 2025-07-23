# productos/views.py
from django.shortcuts import render
from .models import Producto, Categoria

def lista_productos(request):
    # Obtenemos todos los productos y los ordenamos por categoría y luego por nombre
    productos = Producto.objects.select_related('categoria').order_by('categoria__nombre', 'nombre')
    
    # Creamos el contexto para pasar los datos a la plantilla
    context = {
        'productos': productos
    }
    
    # Renderizamos la plantilla con el contexto
    return render(request, 'productos/lista_productos.html', context)
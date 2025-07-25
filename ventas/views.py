# ventas/views.py
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .models import Mesa, Pedido, DetallePedido
from productos.models import Producto
from django.contrib import messages
from .forms import MesaForm 
from django.contrib.auth.decorators import login_required 

@login_required
def panel_mesas_vista(request):
    mesas = Mesa.objects.all().order_by('numero')
    context = {
        'mesas': mesas
    }
    return render(request, 'ventas/panel_mesas.html', context)

# ventas/views.py
@login_required
def abrir_mesa_vista(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)

    # Si la petición es POST, significa que el cajero ha enviado el nombre
    if request.method == 'POST':
        nombre_cliente = request.POST.get('nombre_cliente', f"Mesa {mesa.numero}")

        # Si el nombre viene vacío, le asignamos el nombre de la mesa por defecto
        if not nombre_cliente.strip():
            nombre_cliente = f"Mesa {mesa.numero}"

        # Creamos el nuevo pedido
        nuevo_pedido = Pedido.objects.create(
            mesa=mesa,
            nombre_cliente=nombre_cliente,
            estado='ABIERTO'
        )

        # Cambiamos el estado de la mesa
        mesa.estado = 'OCUPADA'
        mesa.save()

        # Redirigimos a la pantalla de gestión
        return redirect('gestionar_pedido', mesa_id=mesa.id)

    # Si la petición es GET, mostramos el formulario para pedir el nombre
    context = {
        'mesa': mesa
    }
    return render(request, 'ventas/abrir_cuenta.html', context)

@login_required
def gestionar_pedido_vista(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    # Buscamos el pedido que está actualmente ABIERTO para esta mesa
    pedido = Pedido.objects.filter(mesa=mesa, estado='ABIERTO').last()

    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        producto = get_object_or_404(Producto, id=producto_id)
        
        detalle, created = DetallePedido.objects.get_or_create(
            pedido=pedido,
            producto=producto,
            defaults={'precio_venta': producto.precio}
        )
        
        if not created:
            detalle.cantidad += 1
            detalle.save()
        
        pedido.actualizar_total()
        # Redirigimos a la misma página para que vea el pedido actualizado
        return redirect('gestionar_pedido', mesa_id=mesa.id)

    # Si es GET, mostramos los productos y el detalle del pedido actual
    productos_disponibles = Producto.objects.filter(disponible=True).order_by('categoria__nombre')
    context = {
        'mesa': mesa,
        'pedido': pedido,
        'productos': productos_disponibles,
    }
    return render(request, 'ventas/gestionar_pedido.html', context)

@login_required
def eliminar_detalle_vista(request, detalle_id):
    # Usamos POST para asegurarnos de que la eliminación sea intencionada
    if request.method == 'POST':
        detalle = get_object_or_404(DetallePedido, id=detalle_id)
        pedido = detalle.pedido # Guardamos el pedido antes de borrar el detalle
        detalle.delete()
        
        # Actualizamos el total del pedido
        pedido.actualizar_total()
        
        # Redirigimos de vuelta a la página de gestión de ese pedido
        return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)
    # Si no es POST, simplemente redirigimos sin hacer nada
    return redirect('panel_mesas')

@login_required
def actualizar_cantidad_vista(request, detalle_id):
    if request.method == 'POST':
        detalle = get_object_or_404(DetallePedido, id=detalle_id)
        nueva_cantidad = request.POST.get('cantidad')
        
        # Validamos que la cantidad sea un número positivo
        if nueva_cantidad and int(nueva_cantidad) > 0:
            detalle.cantidad = int(nueva_cantidad)
            detalle.save()
            detalle.pedido.actualizar_total() # Actualizamos el total
        
        return redirect('gestionar_pedido', mesa_id=detalle.pedido.mesa.id)
    
    return redirect('panel_mesas')

@login_required
@transaction.atomic
def facturar_pedido_vista(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)

        # --- LÓGICA DE COMPROBACIÓN CORREGIDA ---
        # 1. PRIMERO, revisamos si hay rondas sin resolver. Esta es la prioridad.
        rondas_pendientes = pedido.rondas_bolirana.filter(estado__in=['EN_JUEGO', 'PENDIENTE'])
        if rondas_pendientes.exists():
            messages.error(request, 'No se puede facturar. La cuenta tiene rondas de bolirana sin resolver. Por favor, finalícelas o cancélelas primero.')
            return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)

        # 2. SÓLO SI no hay rondas pendientes, revisamos si el total es cero.
        if pedido.total == 0:
            messages.error(request, 'No se puede facturar una cuenta con total $0. Usa el botón "Cerrar / Cancelar" para liberar la mesa.')
            return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)
        # --- FIN DE LA LÓGICA CORREGIDA ---

        # Si pasa ambas comprobaciones, el resto del código sigue igual
        for detalle in pedido.detalles.all():
            producto = detalle.producto
            if producto.stock < detalle.cantidad:
                messages.error(request, f"No hay stock suficiente para '{producto.nombre}'. Venta no completada.")
                return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)
            
            producto.stock -= detalle.cantidad
            producto.save()

        pedido.actualizar_total()
        pedido.estado = 'FACTURADO'
        pedido.save()
        
        mesa = pedido.mesa
        if mesa:
            mesa.estado = 'LIBRE'
            mesa.save()
            
        messages.success(request, f"El pedido de '{pedido.nombre_cliente}' ha sido facturado exitosamente.")
            
    return redirect('panel_mesas')

@login_required
@transaction.atomic
def cancelar_pedido_vista(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        mesa = pedido.mesa

        # Comprobación de seguridad para rondas sin resolver
        rondas_pendientes = pedido.rondas_bolirana.filter(estado__in=['EN_JUEGO', 'PENDIENTE'])
        if rondas_pendientes.exists():
            messages.error(request, 'No se puede cerrar. La cuenta aún tiene rondas de bolirana sin resolver.')
            return redirect('gestionar_pedido', mesa_id=mesa.id)

        # --- LÓGICA INTELIGENTE NUEVA ---
        if pedido.total > 0:
            # Si la cuenta tiene productos, se anula.
            pedido.estado = 'ANULADO'
            pedido.save()
            messages.warning(request, f"La cuenta de '{pedido.nombre_cliente}' ha sido ANULADA.")
        else:
            # Si la cuenta está en cero, intentamos borrarla.
            # Gracias a on_delete=PROTECT, esto fallará si hay rondas asociadas,
            # pero las rondas NO se borrarán.
            try:
                nombre_cuenta = pedido.nombre_cliente
                pedido.delete()
                messages.info(request, f"La cuenta vacía de '{nombre_cuenta}' ha sido cerrada y eliminada.")
            except Exception:
                # Si no se puede borrar (porque tiene rondas), simplemente la cerramos
                # marcándola como facturada para que no aparezca como abierta.
                pedido.estado = 'FACTURADO'
                pedido.save()
                messages.info(request, f"La cuenta de '{pedido.nombre_cliente}' (solo bolirana) ha sido cerrada.")
        # --- FIN DE LA LÓGICA ---

        # En todos los casos, liberamos la mesa
        if mesa:
            mesa.estado = 'LIBRE'
            mesa.save()

    return redirect('panel_mesas')

@login_required
def agregar_mesa_vista(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Mesa añadida correctamente!')
            return redirect('panel_mesas')
    else:
        form = MesaForm()

    context = {
        'form': form
    }
    return render(request, 'ventas/agregar_mesa.html', context)
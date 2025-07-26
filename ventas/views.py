# ventas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.utils import timezone # <-- Importación clave que faltaba
from productos.models import Producto
from .models import Mesa, Pedido, DetallePedido
from .forms import MesaForm, ItemPersonalizadoForm

@login_required
def panel_mesas_vista(request):
    mesas = Mesa.objects.all().order_by('numero')
    context = {
        'mesas': mesas
    }
    return render(request, 'ventas/panel_mesas.html', context)

@login_required
def abrir_mesa_vista(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    
    if request.method == 'POST':
        nombre_cliente = request.POST.get('nombre_cliente', f"Mesa {mesa.numero}")
        
        if not nombre_cliente.strip():
            nombre_cliente = f"Mesa {mesa.numero}"

        nuevo_pedido = Pedido.objects.create(
            mesa=mesa,
            nombre_cliente=nombre_cliente,
            estado='ABIERTO'
        )
        
        mesa.estado = 'OCUPADA'
        mesa.save()
        
        return redirect('gestionar_pedido', mesa_id=mesa.id)

    context = {
        'mesa': mesa
    }
    return render(request, 'ventas/abrir_cuenta.html', context)

@login_required
def gestionar_pedido_vista(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    pedido = Pedido.objects.filter(mesa=mesa, estado='ABIERTO').first()

    if request.method == 'POST':
        if 'producto_id' in request.POST:
            producto_id = request.POST.get('producto_id')
            producto = get_object_or_404(Producto, id=producto_id)
            
            if pedido:
                detalle, created = DetallePedido.objects.get_or_create(
                    pedido=pedido,
                    producto=producto,
                    defaults={'precio_venta': producto.precio}
                )
                
                if not created:
                    detalle.cantidad += 1
                    detalle.save()
                
                pedido.actualizar_total()
        
        return redirect('gestionar_pedido', mesa_id=mesa.id)

    productos_disponibles = Producto.objects.filter(disponible=True).order_by('categoria__nombre')
    context = {
        'mesa': mesa,
        'pedido': pedido,
        'productos': productos_disponibles,
    }
    return render(request, 'ventas/gestionar_pedido.html', context)


@login_required
def actualizar_cantidad_vista(request, detalle_id):
    if request.method == 'POST':
        detalle = get_object_or_404(DetallePedido, id=detalle_id)
        nueva_cantidad = request.POST.get('cantidad')
        
        if nueva_cantidad and int(nueva_cantidad) > 0:
            detalle.cantidad = int(nueva_cantidad)
            detalle.save()
            detalle.pedido.actualizar_total()
        
        return redirect('gestionar_pedido', mesa_id=detalle.pedido.mesa.id)
    
    return redirect('panel_mesas')

@login_required
def eliminar_detalle_vista(request, detalle_id):
    if request.method == 'POST':
        detalle = get_object_or_404(DetallePedido, id=detalle_id)
        pedido = detalle.pedido
        detalle.delete()
        
        pedido.actualizar_total()
        
        return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)
    return redirect('panel_mesas')

@login_required
@transaction.atomic
def facturar_pedido_vista(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)

        rondas_pendientes = pedido.rondas_bolirana.filter(estado__in=['EN_JUEGO', 'PENDIENTE'])
        if rondas_pendientes.exists():
            messages.error(request, 'No se puede facturar. La cuenta tiene rondas de bolirana sin resolver.')
            return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)

        if pedido.total == 0:
            messages.error(request, 'No se puede facturar una cuenta con total $0. Usa el botón "Cerrar / Cancelar" para liberar la mesa.')
            return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)

        for detalle in pedido.detalles.all():
            if detalle.producto:
                producto = detalle.producto
                if producto.stock < detalle.cantidad:
                    messages.error(request, f"No hay stock suficiente para '{producto.nombre}'. Venta no completada.")
                    return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)
                
                producto.stock -= detalle.cantidad
                producto.save()

        pedido.actualizar_total()
        pedido.estado = 'FACTURADO'
        pedido.fecha_facturacion = timezone.now()
        pedido.save()
        
        mesa = pedido.mesa
        if mesa:
            mesa.estado = 'LIBRE'
            mesa.save()
            
        messages.success(request, f"El pedido de '{pedido.nombre_cliente}' ha sido facturado exitosamente.")
            
    return redirect('panel_mesas')

# ventas/views.py
@login_required
@transaction.atomic
def cancelar_pedido_vista(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        mesa = pedido.mesa

        # Comprobación de seguridad para rondas sin resolver (no cambia)
        rondas_pendientes = pedido.rondas_bolirana.filter(estado__in=['EN_JUEGO', 'PENDIENTE'])
        if rondas_pendientes.exists():
            messages.error(request, 'No se puede cerrar. La cuenta aún tiene rondas de bolirana sin resolver.')
            return redirect('gestionar_pedido', mesa_id=mesa.id)

        # --- LÓGICA INTELIGENTE CORREGIDA ---
        if pedido.total > 0:
            # Caso 1: La cuenta tiene productos. Se anula.
            pedido.estado = 'ANULADO'
            pedido.save()
            messages.warning(request, f"La cuenta de '{pedido.nombre_cliente}' ha sido ANULADA.")
        else:
            # Caso 2: La cuenta está en cero.
            if pedido.rondas_bolirana.exists():
                # Si tuvo rondas, la cerramos para no perder el historial.
                pedido.estado = 'CERRADO'
                pedido.save()
                # CORRECCIÓN: Añadimos 'request'
                messages.info(request, f"La cuenta de '{pedido.nombre_cliente}' (solo bolirana) ha sido cerrada.")
            else:
                # Si no tuvo ni productos ni rondas, fue un error. La borramos.
                nombre_cuenta = pedido.nombre_cliente
                pedido.delete()
                # CORRECCIÓN: Añadimos 'request'
                messages.info(request, f"La cuenta vacía de '{nombre_cuenta}' ha sido eliminada.")
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

@login_required
def agregar_item_personalizado_vista(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = ItemPersonalizadoForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            DetallePedido.objects.create(
                pedido=pedido,
                descripcion_personalizada=datos['descripcion'],
                cantidad=datos['cantidad'],
                precio_venta=datos['precio_unitario']
            )
            pedido.actualizar_total()
            messages.success(request, "Item personalizado añadido a la cuenta.")
            try:
                mesa_id = pedido.mesa.id
                return redirect('gestionar_pedido', mesa_id=mesa_id)
            except AttributeError:
                return redirect('panel_mesas')
    else:
        form = ItemPersonalizadoForm()
    
    context = {'form': form, 'pedido': pedido}
    return render(request, 'ventas/agregar_item_personalizado.html', context)
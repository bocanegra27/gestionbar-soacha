# juegos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ventas.models import Pedido, DetallePedido
from .models import RondaBolirana
from .forms import DetalleRondaFormSet, FinalizarRondaForm

@login_required
def iniciar_ronda_vista(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        formset = DetalleRondaFormSet(request.POST, prefix='detalles')
        if formset.is_valid():
            ronda = RondaBolirana.objects.create(pedido=pedido, estado='EN_JUEGO')
            for detalle_form in formset:
                if detalle_form.is_valid() and detalle_form.has_changed() and not detalle_form.cleaned_data.get('DELETE', False):
                    detalle = detalle_form.save(commit=False)
                    detalle.ronda = ronda
                    detalle.save()
            messages.success(request, 'Ronda iniciada. ¡Ahora a jugar!')
            return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)
    else:
        formset = DetalleRondaFormSet(prefix='detalles')

    context = {
        'formset': formset,
        'pedido': pedido
    }
    return render(request, 'juegos/iniciar_ronda.html', context)

@login_required
def finalizar_ronda_vista(request, ronda_id):
    ronda = get_object_or_404(RondaBolirana, id=ronda_id, estado='EN_JUEGO')
    pedido = ronda.pedido

    if request.method == 'POST':
        form = FinalizarRondaForm(request.POST, instance=ronda)
        if form.is_valid():
            ronda_finalizada = form.save(commit=False)
            ronda_finalizada.estado = 'PENDIENTE'
            ronda_finalizada.save()
            messages.success(request, f'Ronda finalizada. Perdedor: {ronda_finalizada.nombre_perdedor}.')
            return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)
    else:
        form = FinalizarRondaForm(instance=ronda)

    context = {
        'form': form,
        'ronda': ronda
    }
    return render(request, 'juegos/finalizar_ronda.html', context)

@login_required
def pagar_ronda_vista(request, ronda_id):
    ronda = get_object_or_404(RondaBolirana, id=ronda_id, estado='PENDIENTE')
    pedido = ronda.pedido

    if request.method == 'POST':
        
        # --- LÓGICA DE STOCK NUEVA ---
        # 1. Comprobamos si hay stock suficiente para toda la ronda
        for detalle_ronda in ronda.detalles.all():
            producto = detalle_ronda.producto
            if producto.stock < detalle_ronda.cantidad:
                # Si un producto no tiene stock, mostramos un error y detenemos todo
                messages.error(request, f"No hay stock suficiente para '{producto.nombre}' en la ronda. La ronda no ha sido pagada.")
                return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)

        # 2. Si hay stock para todo, ahora sí lo descontamos
        for detalle_ronda in ronda.detalles.all():
            producto = detalle_ronda.producto
            producto.stock -= detalle_ronda.cantidad
            producto.save()
        # --- FIN DE LA LÓGICA DE STOCK ---

        # Si todo fue bien, marcamos la ronda como pagada
        ronda.estado = 'PAGADA'
        ronda.save()
        
        # El total del pedido principal NO se actualiza, lo cual es correcto.
        
        messages.success(request, f'La ronda de {ronda.nombre_perdedor} ha sido pagada y el stock ha sido actualizado.')
        return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)
    
    return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)
# --- FUNCIÓN NUEVA QUE FALTABA ---
@login_required
def cancelar_ronda_vista(request, ronda_id):
    ronda = get_object_or_404(RondaBolirana, id=ronda_id)
    pedido = ronda.pedido
    if request.method == 'POST':
        ronda.delete()
        messages.info(request, 'La ronda de bolirana ha sido cancelada.')
    return redirect('gestionar_pedido', mesa_id=pedido.mesa.id)
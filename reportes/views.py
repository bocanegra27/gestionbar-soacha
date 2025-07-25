# reportes/views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from ventas.models import Pedido
from juegos.models import RondaBolirana
from .models import CierreCaja
from datetime import datetime
from decimal import Decimal

@login_required
def reporte_diario_vista(request):
    fecha_seleccionada_str = request.GET.get('fecha', timezone.now().strftime('%Y-%m-%d'))
    fecha_seleccionada = datetime.strptime(fecha_seleccionada_str, '%Y-%m-%d').date()

    pedidos_facturados = Pedido.objects.filter(
        estado='FACTURADO',
        fecha_hora__date=fecha_seleccionada
    ).order_by('fecha_hora')
    total_pedidos = sum(pedido.total for pedido in pedidos_facturados)

    rondas_pagadas = RondaBolirana.objects.filter(
        estado='PAGADA',
        fecha_creacion__date=fecha_seleccionada
    ).order_by('fecha_creacion')
    total_rondas = sum(ronda.get_total() for ronda in rondas_pagadas)

    total_ventas_dia = total_pedidos + total_rondas

    context = {
        'pedidos': pedidos_facturados,
        'rondas_pagadas': rondas_pagadas,
        'total_ventas': total_ventas_dia,
        'fecha_seleccionada': fecha_seleccionada,
    }
    return render(request, 'reportes/reporte_diario.html', context)

@login_required
def cierre_caja_vista(request):
    hoy = timezone.now().date()
    cierre_existente = CierreCaja.objects.filter(fecha=hoy).first()

    # Calculamos el total de ventas del sistema para hoy (incluyendo rondas)
    total_pedidos = sum(p.total for p in Pedido.objects.filter(estado='FACTURADO', fecha_hora__date=hoy))
    total_rondas = sum(r.get_total() for r in RondaBolirana.objects.filter(estado='PAGADA', fecha_creacion__date=hoy))
    total_sistema = total_pedidos + total_rondas

    if request.method == 'POST':
        if not cierre_existente:
            total_contado_str = request.POST.get('total_contado')
            observaciones = request.POST.get('observaciones')
            
            if total_contado_str:
                total_contado = Decimal(total_contado_str)
                diferencia = total_contado - total_sistema
                
                CierreCaja.objects.create(
                    fecha=hoy,
                    total_ventas_sistema=total_sistema,
                    total_efectivo_contado=total_contado,
                    diferencia=diferencia,
                    responsable=request.user,
                    observaciones=observaciones
                )
                return redirect('reporte_diario')

    context = {
        'hoy': hoy,
        'total_sistema': total_sistema,
        'cierre_existente': cierre_existente
    }
    return render(request, 'reportes/cierre_caja.html', context)
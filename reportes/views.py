# reportes/views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from ventas.models import Pedido
from juegos.models import RondaBolirana
from .models import CierreCaja
from datetime import datetime, timedelta
from decimal import Decimal

@login_required
def reporte_diario_vista(request):
    # --- CAMBIO 1: Usamos localtime para obtener la fecha correcta en Colombia ---
    fecha_actual_colombia = timezone.localtime(timezone.now()).date()
    fecha_seleccionada_str = request.GET.get('fecha', fecha_actual_colombia.strftime('%Y-%m-%d'))
    # --- FIN DEL CAMBIO ---

    fecha_seleccionada = datetime.strptime(fecha_seleccionada_str, '%Y-%m-%d').date()

    # Definimos el "día de negocio" (6 AM a 5:59 AM del día siguiente)
    inicio_dia = timezone.make_aware(datetime.combine(fecha_seleccionada, datetime.min.time())) + timedelta(hours=6)
    fin_dia = inicio_dia + timedelta(days=1)

    # --- CAMBIO 2: Usamos fecha_facturacion y fecha_pago para mayor precisión ---
    pedidos_facturados = Pedido.objects.filter(
        estado='FACTURADO',
        fecha_facturacion__range=(inicio_dia, fin_dia)
    ).order_by('fecha_facturacion')
    total_pedidos = sum(pedido.total for pedido in pedidos_facturados)

    rondas_pagadas = RondaBolirana.objects.filter(
        estado='PAGADA',
        fecha_pago__range=(inicio_dia, fin_dia)
    ).order_by('fecha_pago')
    total_rondas = sum(ronda.get_total() for ronda in rondas_pagadas)
    # --- FIN DEL CAMBIO ---

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
    # --- CAMBIO 3: Usamos localtime para determinar el día de negocio ---
    ahora = timezone.localtime(timezone.now())
    # --- FIN DEL CAMBIO ---

    if ahora.hour < 6:
        dia_negocio = ahora.date() - timedelta(days=1)
    else:
        dia_negocio = ahora.date()

    inicio_dia = timezone.make_aware(datetime.combine(dia_negocio, datetime.min.time())) + timedelta(hours=6)
    fin_dia = inicio_dia + timedelta(days=1)
    
    cierre_existente = CierreCaja.objects.filter(fecha=dia_negocio).first()

    # Usamos los campos de fecha de cierre para mayor precisión
    total_pedidos = sum(p.total for p in Pedido.objects.filter(estado='FACTURADO', fecha_facturacion__range=(inicio_dia, fin_dia)))
    total_rondas = sum(r.get_total() for r in RondaBolirana.objects.filter(estado='PAGADA', fecha_pago__range=(inicio_dia, fin_dia)))
    total_sistema = total_pedidos + total_rondas

    if request.method == 'POST':
        if not cierre_existente:
            total_contado_str = request.POST.get('total_contado')
            observaciones = request.POST.get('observaciones')
            
            if total_contado_str:
                total_contado = Decimal(total_contado_str)
                diferencia = total_contado - total_sistema
                
                CierreCaja.objects.create(
                    fecha=dia_negocio,
                    total_ventas_sistema=total_sistema,
                    total_efectivo_contado=total_contado,
                    diferencia=diferencia,
                    responsable=request.user,
                    observaciones=observaciones
                )
                return redirect('reporte_diario')

    context = {
        'hoy': dia_negocio,
        'total_sistema': total_sistema,
        'cierre_existente': cierre_existente
    }
    return render(request, 'reportes/cierre_caja.html', context)
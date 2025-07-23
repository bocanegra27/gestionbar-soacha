# reportes/views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from ventas.models import Pedido
from .models import CierreCaja
from datetime import datetime
from decimal import Decimal

@login_required
def reporte_diario_vista(request):
    # Por defecto, mostramos el reporte del día de hoy
    fecha_seleccionada_str = request.GET.get('fecha', timezone.now().strftime('%Y-%m-%d'))
    fecha_seleccionada = datetime.strptime(fecha_seleccionada_str, '%Y-%m-%d').date()

    # Filtramos los pedidos que fueron facturados en la fecha seleccionada
    pedidos_facturados = Pedido.objects.filter(
        estado='FACTURADO',
        fecha_hora__date=fecha_seleccionada
    ).order_by('fecha_hora')

    # Calculamos el total de las ventas del día
    total_ventas = sum(pedido.total for pedido in pedidos_facturados)

    context = {
        'pedidos': pedidos_facturados,
        'total_ventas': total_ventas,
        'fecha_seleccionada': fecha_seleccionada,
    }
    return render(request, 'reportes/reporte_diario.html', context)

@login_required # Solo usuarios logueados pueden acceder
def cierre_caja_vista(request):
    hoy = timezone.now().date()
    
    # Comprobamos si ya se hizo un cierre para hoy
    cierre_existente = CierreCaja.objects.filter(fecha=hoy).first()

    # Calculamos el total de ventas del sistema para hoy
    ventas_hoy = Pedido.objects.filter(estado='FACTURADO', fecha_hora__date=hoy)
    total_sistema = sum(p.total for p in ventas_hoy)

    if request.method == 'POST':
        # Si no hay cierre existente, procesamos el formulario
        if not cierre_existente:
            total_contado_str = request.POST.get('total_contado')
            observaciones = request.POST.get('observaciones')
            
            if total_contado_str:
                total_contado = Decimal(total_contado_str)
                diferencia = total_contado - total_sistema
                
                # Creamos el registro del cierre de caja
                CierreCaja.objects.create(
                    fecha=hoy,
                    total_ventas_sistema=total_sistema,
                    total_efectivo_contado=total_contado,
                    diferencia=diferencia,
                    responsable=request.user,
                    observaciones=observaciones
                )
                return redirect('reporte_diario') # Redirigimos al reporte al finalizar

    context = {
        'hoy': hoy,
        'total_sistema': total_sistema,
        'cierre_existente': cierre_existente
    }
    return render(request, 'reportes/cierre_caja.html', context)


# ventas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La URL raíz de 'pedidos/' ahora será nuestro panel de mesas
    path('', views.panel_mesas_vista, name='panel_mesas'),
    path('mesas/agregar/', views.agregar_mesa_vista, name='agregar_mesa'),
    # URL para abrir la cuenta de una mesa específica
    path('mesa/<int:mesa_id>/abrir/', views.abrir_mesa_vista, name='abrir_mesa'),
    # URL para gestionar el pedido de una mesa específica
    path('mesa/<int:mesa_id>/gestionar/', views.gestionar_pedido_vista, name='gestionar_pedido'),
    # --- LÍNEAS NUEVAS ---
    path('detalle/<int:detalle_id>/actualizar/', views.actualizar_cantidad_vista, name='actualizar_cantidad'),
    path('detalle/<int:detalle_id>/eliminar/', views.eliminar_detalle_vista, name='eliminar_detalle'),
    # --- LÍNEAS NUEVAS ---
    path('pedido/<int:pedido_id>/facturar/', views.facturar_pedido_vista, name='facturar_pedido'),
    path('pedido/<int:pedido_id>/cancelar/', views.cancelar_pedido_vista, name='cancelar_pedido'),
    path('pedido/<int:pedido_id>/agregar_item/', views.agregar_item_personalizado_vista, name='agregar_item_personalizado'),

]
# juegos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('iniciar/<int:pedido_id>/', views.iniciar_ronda_vista, name='iniciar_ronda'),
    path('finalizar/<int:ronda_id>/', views.finalizar_ronda_vista, name='finalizar_ronda'),
    path('pagar/<int:ronda_id>/', views.pagar_ronda_vista, name='pagar_ronda'),
    path('cancelar/<int:ronda_id>/', views.cancelar_ronda_vista, name='cancelar_ronda'),
]
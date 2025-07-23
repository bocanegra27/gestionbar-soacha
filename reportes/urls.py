# reportes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('diario/', views.reporte_diario_vista, name='reporte_diario'),
    path('cierre/', views.cierre_caja_vista, name='cierre_caja'), # <-- LÍNEA NUEVA
]
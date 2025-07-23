# gestion_bar/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import login_inteligente_vista

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pedidos/', include('ventas.urls')),
    path('reportes/', include('reportes.urls')),

    # --- RUTAS DE AUTENTICACIÓN SIMPLIFICADAS ---
    path('login/', login_inteligente_vista, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
# gestion_bar/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import login_inteligente_vista

# --- Importaciones nuevas para archivos estáticos ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pedidos/', include('ventas.urls')),
    path('reportes/', include('reportes.urls')),
    path('juegos/', include('juegos.urls')), # Asegúrate de que esta línea esté

    path('login/', login_inteligente_vista, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

# --- LÍNEAS NUEVAS ---
# Esto le dice a Django que sirva los archivos estáticos (como el CSS del admin)
# solo cuando estemos en modo de desarrollo (DEBUG = True).
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# gestion_bar/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

def login_inteligente_vista(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # La lógica de redirección inteligente
            if user.is_staff:
                return redirect('admin:index') # Redirige al admin
            else:
                return redirect('panel_mesas') # Redirige al cajero
    else:
        form = AuthenticationForm()

    # Si no es POST o el form no es válido, muestra la página de login
    return render(request, 'login.html', {'form': form})
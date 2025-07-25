# juegos/forms.py
from django import forms
from django.forms import formset_factory
from .models import RondaBolirana, DetalleRonda
from productos.models import Producto

class DetalleRondaForm(forms.ModelForm):
    class Meta:
        model = DetalleRonda
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'shadow border rounded w-full py-2 px-3 text-gray-700'}),
            'cantidad': forms.NumberInput(attrs={'class': 'shadow border rounded w-full py-2 px-3 text-gray-700', 'min': '1'}),
        }

# Creamos un "formset" para la lista de productos
DetalleRondaFormSet = formset_factory(DetalleRondaForm, extra=1, can_delete=True)

class FinalizarRondaForm(forms.ModelForm):
    class Meta:
        model = RondaBolirana
        fields = ['nombre_perdedor']
        labels = {
            'nombre_perdedor': 'Nombre del jugador que perdió',
        }
        widgets = {
            'nombre_perdedor': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        }
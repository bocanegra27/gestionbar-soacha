# ventas/forms.py
from django import forms
from .models import Mesa # <-- CAMBIO: La importación ahora está aquí arriba

class MesaForm(forms.ModelForm):
    # Este es el formulario que ya teníamos para añadir mesas.
    # Lo dejamos aquí para mantener todo organizado.
    class Meta:
        model = Mesa
        fields = ['numero']
        labels = {
            'numero': 'Número de la nueva mesa',
        }
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        }

# --- FORMULARIO NUEVO ---
class ItemPersonalizadoForm(forms.Form):
    descripcion = forms.CharField(
        label="Descripción del Item",
        widget=forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
    )
    cantidad = forms.IntegerField(
        label="Cantidad",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
    )
    precio_unitario = forms.DecimalField(
        label="Precio Unitario",
        widget=forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
    )
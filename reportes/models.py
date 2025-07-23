# reportes/models.py
from django.db import models
from django.contrib.auth.models import User

class CierreCaja(models.Model):
    fecha = models.DateField(unique=True)
    total_ventas_sistema = models.DecimalField(max_digits=10, decimal_places=2)
    total_efectivo_contado = models.DecimalField(max_digits=10, decimal_places=2)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2)
    responsable = models.ForeignKey(User, on_delete=models.PROTECT)
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cierre del {self.fecha} - Diferencia: {self.diferencia}"
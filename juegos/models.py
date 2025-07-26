# juegos/models.py
from django.db import models
from ventas.models import Pedido
from productos.models import Producto

class RondaBolirana(models.Model):
    ESTADO_CHOICES = [
        ('EN_JUEGO', 'En Juego'),
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADA', 'Pagada'),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT, related_name='rondas_bolirana')
    nombre_perdedor = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='EN_JUEGO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)

    def get_total(self):
        """Calcula el valor total de la ronda sumando el precio de sus productos."""
        total = 0
        for detalle in self.detalles.all():
            total += detalle.cantidad * detalle.producto.precio
        return total

    

    def __str__(self):
        if self.nombre_perdedor:
            return f"Ronda de {self.nombre_perdedor} para el pedido #{self.pedido.id}"
        return f"Ronda en juego para el pedido #{self.pedido.id}"

class DetalleRonda(models.Model):
    ronda = models.ForeignKey(RondaBolirana, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
from django.db import models
from productos.models import Producto
from django.contrib.auth.models import User

class Mesa(models.Model):
    ESTADO_CHOICES = [
        ('LIBRE', 'Libre'),
        ('OCUPADA', 'Ocupada'),
    ]
    numero = models.IntegerField(unique=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='LIBRE')

    def __str__(self):
        return f"Mesa #{self.numero} ({self.get_estado_display()})"
        # --- MÉTODO NUEVO ---
    def get_pedido_abierto(self):
        """Devuelve el primer pedido con estado 'ABIERTO' para esta mesa."""
        return self.pedidos.filter(estado='ABIERTO').first()
    # --- FIN MÉTODO NUEVO ---


class Pedido(models.Model):
    # CAMBIO 1: La mesa ahora es opcional
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    
    # CAMBIO 2: Se añade un campo para el nombre del cliente/pedido
    nombre_cliente = models.CharField(max_length=100, default="Pedido sin nombre")

    ESTADO_CHOICES = [
        ('ABIERTO', 'Abierto'),
        ('FACTURADO', 'Facturado'),
        ('ANULADO', 'Anulado'),
    ]
    
    fecha_hora = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ABIERTO')

    def actualizar_total(self):
        """Calcula el total sumando los subtotales de todos los detalles."""
        nuevo_total = sum(item.cantidad * item.precio_venta for item in self.detalles.all())
        self.total = nuevo_total
        self.save()

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    # CAMBIO 3: El __str__ ahora es más descriptivo
    def __str__(self):
        if self.mesa:
            return f"Pedido de {self.mesa} - ({self.get_estado_display()})"
        return f"Pedido de '{self.nombre_cliente}' - ({self.get_estado_display()})"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido #{self.pedido.id}"
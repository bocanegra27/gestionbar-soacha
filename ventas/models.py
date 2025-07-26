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
    
    def get_pedido_abierto(self):
        """Devuelve el primer pedido con estado 'ABIERTO' para esta mesa."""
        return self.pedidos.filter(estado='ABIERTO').first()


class Pedido(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    nombre_cliente = models.CharField(max_length=100, default="Pedido sin nombre")

    ESTADO_CHOICES = [
        ('ABIERTO', 'Abierto'),
        ('FACTURADO', 'Facturado'),
        ('ANULADO', 'Anulado'),
        ('CERRADO', 'Cerrado'),
    ]
    
    fecha_hora = models.DateTimeField(auto_now_add=True)
    fecha_facturacion = models.DateTimeField(null=True, blank=True)
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

    def __str__(self):
        if self.mesa:
            return f"Pedido de {self.mesa} - ({self.get_estado_display()})"
        return f"Pedido de '{self.nombre_cliente}' - ({self.get_estado_display()})"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    
    # --- CAMBIO 1: Hacemos el producto opcional ---
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, null=True, blank=True)
    
    # --- CAMBIO 2: Añadimos un campo para la descripción personalizada ---
    descripcion_personalizada = models.CharField(max_length=255, null=True, blank=True)
    
    cantidad = models.PositiveIntegerField(default=1)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"

    # --- CAMBIO 3: Añadimos un método para obtener el nombre ---
    def get_nombre(self):
        """Devuelve el nombre del producto o la descripción personalizada."""
        if self.producto:
            return self.producto.nombre
        return self.descripcion_personalizada

    def __str__(self):
        # Usamos el nuevo método para que el admin se vea bien
        return f"{self.cantidad} x {self.get_nombre()} en Pedido #{self.pedido.id}"
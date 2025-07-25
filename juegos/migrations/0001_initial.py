# Generated by Django 5.2.4 on 2025-07-24 22:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('productos', '0002_producto_stock'),
        ('ventas', '0003_pedido_nombre_cliente_alter_pedido_mesa'),
    ]

    operations = [
        migrations.CreateModel(
            name='RondaBolirana',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_perdedor', models.CharField(blank=True, max_length=100, null=True)),
                ('estado', models.CharField(choices=[('EN_JUEGO', 'En Juego'), ('PENDIENTE', 'Pendiente de Pago'), ('PAGADA', 'Pagada')], default='EN_JUEGO', max_length=10)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rondas_bolirana', to='ventas.pedido')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleRonda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='productos.producto')),
                ('ronda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='juegos.rondabolirana')),
            ],
        ),
    ]

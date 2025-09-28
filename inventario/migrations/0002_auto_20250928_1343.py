# Reemplaza el contenido del nuevo archivo de migración con esto.

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ganado',
            name='fecha_fallecimiento',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de Fallecimiento'),
        ),
        migrations.AddField(
            model_name='ganado',
            name='razon_fallecimiento',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Razón del Fallecimiento'),
        ),
        migrations.AddField(
            model_name='ganado',
            name='fecha_venta',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de Venta'),
        ),
        migrations.AddField(
            model_name='ganado',
            name='valor_venta',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Valor de Venta'),
        ),
        migrations.AddField(
            model_name='ganado',
            name='razon_venta',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Razón de la Venta'),
        ),
        migrations.AddField(
            model_name='ganado',
            name='comprador',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Comprador'),
        ),
        migrations.AddField(
            model_name='ganado',
            name='comprador_telefono',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono del Comprador'),
        ),
    ]
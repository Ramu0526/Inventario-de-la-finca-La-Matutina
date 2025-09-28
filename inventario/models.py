# inventario/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField
from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta

# inventario/models.py

class Producto(models.Model):
    class UnidadMedida(models.TextChoices):
        UNIDADES = 'U', 'Unidades'
        KILOGRAMOS = 'Kg', 'Kilogramos (Kg)'
        LITROS = 'L', 'Litros (L)'

    # AÑADE ESTA SECCIÓN PARA EL ESTADO
    class EstadoProducto(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        APARTADO = 'APARTADO', 'Apartado'
        VENDIDO = 'VENDIDO', 'Vendido'

    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey('caracteristicas.Categoria', on_delete=models.SET_NULL, null=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    unidad_medida = models.CharField(max_length=2, choices=UnidadMedida.choices, default=UnidadMedida.UNIDADES)
    
    # AÑADE EL NUEVO CAMPO 'estado'
    estado = models.CharField(max_length=10, choices=EstadoProducto.choices, default=EstadoProducto.DISPONIBLE)

    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    ubicaciones = models.ManyToManyField('caracteristicas.Ubicacion', blank=True, related_name="productos_ubicados")
    fecha_produccion = models.DateField(default=timezone.now)
    fecha_venta = models.DateField(null=True, blank=True)
    imagen = CloudinaryField('image', folder='productos', null=True, blank=True)
    descripcion = models.TextField(max_length=1000, blank=True, null=True, help_text="Descripción detallada del producto.")
    compradores = models.ManyToManyField('Comprador', through='VentaProducto', blank=True, related_name='productos_comprados')

    @property
    def precio_total(self):
        if self.cantidad is not None and self.precio is not None:
            return self.cantidad * self.precio
        return 0

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.get_unidad_medida_display()})"

class Animal(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Tipo de Animal'
        verbose_name_plural = 'Tipos de Animales'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    
class Ganado(models.Model):
    class GeneroAnimal(models.TextChoices):
        MACHO = 'M', 'Macho'
        HEMBRA = 'H', 'Hembra'

    class EstadoAnimal(models.TextChoices):
        VIVO = 'VIVO', 'Vivo'
        FALLECIDO = 'FALLECIDO', 'Fallecido'
        VENDIDO = 'VENDIDO', 'Vendido'

    class TipoPene(models.TextChoices):
        NATURAL = 'NATURAL', 'Natural'
        INSEMINACION = 'INSEMINACION', 'Inseminación'
        ARTIFICIAL = 'ARTIFICIAL', 'Artificial'
        NO_APLICA = 'NO_APLICA', 'No Aplica'

    class EstadoSalud(models.TextChoices):
        ENFERMA = 'ENFERMA', 'Enferma'
        TRATAMIENTO = 'TRATAMIENTO', 'En Tratamiento'
        RECUPERANDOSE = 'RECUPERANDOSE', 'Recuperándose'
        CURADA = 'CURADA', 'Curada'
        NO_TIENE_NADA = 'NO_TIENE_NADA', 'No tiene nada'

    class Crecimiento(models.TextChoices):
        MENOR = 'MENOR', 'Menor'
        ADULTO = 'ADULTO', 'Adulto'

    identificador = models.CharField(max_length=50, unique=True, help_text="Ej: Arete N° 123")
    animal = models.ForeignKey('Animal', on_delete=models.SET_NULL, null=True, verbose_name="Tipo de Animal")
    raza = models.CharField("Raza", max_length=100, blank=True, help_text="Ej: Holstein, Angus")
    genero = models.CharField(max_length=1, choices=GeneroAnimal.choices, default=GeneroAnimal.HEMBRA)
    peso_kg = models.DecimalField("Peso (Kg)", max_digits=7, decimal_places=2, null=True, blank=True)
    
    crecimiento = models.CharField("Crecimiento", max_length=10, choices=Crecimiento.choices, default=Crecimiento.MENOR)

    fecha_nacimiento = models.DateField()
    estado = models.CharField(max_length=10, choices=EstadoAnimal.choices, default=EstadoAnimal.VIVO)
    estado_salud = models.CharField(max_length=20, choices=EstadoSalud.choices, default=EstadoSalud.NO_TIENE_NADA)
    
    peñe = models.CharField("Tipo de Peñe", max_length=15, choices=TipoPene.choices, default=TipoPene.NO_APLICA)
    fecha_peñe = models.DateField("Fecha de Peñe", null=True, blank=True)
    descripcion_peñe = models.TextField("Descripción del Peñe", max_length=1000, blank=True, null=True)

    fecha_fallecimiento = models.DateField("Fecha de Fallecimiento", null=True, blank=True)
    razon_fallecimiento = models.TextField("Razón del Fallecimiento", max_length=1000, blank=True, null=True)
    
    fecha_venta = models.DateField("Fecha de Venta", null=True, blank=True)
    valor_venta = models.DecimalField("Valor de Venta", max_digits=10, decimal_places=2, null=True, blank=True)
    razon_venta = models.TextField("Razón de la Venta", max_length=1000, blank=True, null=True)
    comprador = models.CharField("Comprador", max_length=100, blank=True, null=True)
    comprador_telefono = models.CharField("Teléfono del Comprador", max_length=20, blank=True, null=True)

    imagen = CloudinaryField('image', folder='ganado', null=True, blank=True)
    descripcion = models.TextField(max_length=1000, blank=True, null=True, help_text="Notas o descripción del animal.")
    
    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return "Fecha no registrada"
        hoy = datetime.date.today()
        diferencia = relativedelta(hoy, self.fecha_nacimiento)
        return f"{diferencia.years} años, {diferencia.months} meses"

    def __str__(self):
        animal_display = self.animal.nombre if self.animal else "[Sin tipo de animal]"
        return f"{self.identificador} - {animal_display}"

class Medicamento(models.Model):
    class UnidadMedida(models.TextChoices):
        UNIDAD = 'U', 'Unidad'
        KILOGRAMOS = 'Kg', 'Kilogramos (Kg)'
        GRAMOS = 'g', 'Gramos (g)'
        LITROS = 'L', 'Litros (L)'
        MILILITROS = 'ml', 'Mililitros (ml)'

    nombre = models.CharField(max_length=100)
    cantidad_ingresada = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    cantidad_usada = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    unidad_medida = models.CharField(max_length=2, choices=UnidadMedida.choices, default=UnidadMedida.UNIDAD)
    categoria = models.ForeignKey('caracteristicas.Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    ubicaciones = models.ManyToManyField('caracteristicas.Ubicacion', blank=True, related_name="medicamentos_ubicados")
    proveedores = models.ManyToManyField('caracteristicas.Proveedor', blank=True, related_name='medicamentos')
    fecha_compra = models.DateField(default=timezone.now)
    fecha_ingreso = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    imagen = CloudinaryField('image', folder='medicamentos', null=True, blank=True)
    descripcion = models.TextField(max_length=1000, blank=True, null=True, help_text="Descripción y notas sobre el medicamento.")
    
    @property
    def cantidad_restante(self):
        return self.cantidad_ingresada - self.cantidad_usada
    
    def __str__(self): 
        return self.nombre


class Vacuna(models.Model):
    class UnidadMedida(models.TextChoices):
        GRAMOS = 'g', 'Gramos (g)'
        MILILITROS = 'ml', 'Mililitros (ml)'
        KILOGRAMOS = 'Kg', 'Kilogramos (Kg)'
        LITROS = 'L', 'Litros (L)'
        UNIDAD = 'U', 'Unidad'

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100, blank=True)
    etiquetas = models.ManyToManyField('caracteristicas.Etiqueta', blank=True)
    disponible = models.BooleanField(default=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    cantidad = models.DecimalField("Cantidad", max_digits=10, decimal_places=2, default=0.0)
    unidad_medida = models.CharField(max_length=2, choices=UnidadMedida.choices, default=UnidadMedida.UNIDAD)
    
    dosis_crecimiento = models.CharField("Dosis por Crecimiento", max_length=100, blank=True)
    dosis_edad = models.CharField("Dosis por Edad", max_length=100, blank=True)
    dosis_peso = models.CharField("Dosis por Peso", max_length=100, blank=True)
    
    fecha_compra = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    
    ubicaciones = models.ManyToManyField('caracteristicas.Ubicacion', blank=True, related_name="vacunas_ubicadas")
    proveedores = models.ManyToManyField('caracteristicas.Proveedor', blank=True, related_name='vacunas')
    
    descripcion = models.TextField(max_length=1000, blank=True, null=True, help_text="Descripción de la vacuna.")
    imagen = CloudinaryField('image', folder='vacunas', null=True, blank=True)

    class Meta:
        verbose_name = 'Vacuna'
        verbose_name_plural = 'Vacunas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class RegistroVacunacion(models.Model):
    ganado = models.ForeignKey('Ganado', on_delete=models.CASCADE, related_name='vacunaciones')
    vacuna = models.ForeignKey('Vacuna', on_delete=models.CASCADE, related_name='registros')
    fecha_aplicacion = models.DateField(default=timezone.now)
    fecha_proxima_dosis = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Registro de Vacunación'
        verbose_name_plural = 'Registros de Vacunación'
        ordering = ['-fecha_aplicacion']

    def __str__(self):
        return f"Vacunación de {self.ganado.identificador} con {self.vacuna.nombre}"


class RegistroMedicamento(models.Model):
    ganado = models.ForeignKey('Ganado', on_delete=models.CASCADE, related_name='medicamentos_aplicados')
    medicamento = models.ForeignKey('Medicamento', on_delete=models.CASCADE, related_name='registros_aplicacion')
    fecha_aplicacion = models.DateField(default=timezone.now)
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Registro de Medicamento'
        verbose_name_plural = 'Registros de Medicamentos'
        ordering = ['-fecha_aplicacion']

    def __str__(self):
        return f"Aplicación de {self.medicamento.nombre} a {self.ganado.identificador}"


class Alimento(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Heno, Silo de maíz, Sal mineral")
    categoria = models.ForeignKey('caracteristicas.Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    etiquetas = models.ManyToManyField('caracteristicas.Etiqueta', blank=True)
    cantidad_kg_ingresada = models.DecimalField("Cantidad (Kg)", max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)], default=0.0)
    cantidad_kg_usada = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0.0)])
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    ubicaciones = models.ManyToManyField('caracteristicas.Ubicacion', blank=True, related_name="alimentos_ubicados")
    proveedores = models.ManyToManyField('caracteristicas.Proveedor', blank=True, related_name='alimentos')
    fecha_compra = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(default=datetime.date.today)
    imagen = CloudinaryField('image', folder='alimentos', null=True, blank=True)
    descripcion = models.TextField(max_length=1000, blank=True, null=True, help_text="Descripción del alimento.")

    @property
    def cantidad_kg_restante(self):
        return self.cantidad_kg_ingresada - self.cantidad_kg_usada

    def __str__(self):
        return self.nombre
    
class ControlPlaga(models.Model):
    class UnidadMedida(models.TextChoices):
        LITROS = 'L', 'Litros (L)'
        MILILITROS = 'ml', 'Mililitros (ml)'
        KILOGRAMOS = 'Kg', 'Kilogramos (Kg)'
        GRAMOS = 'g', 'Gramos (g)'

    nombre_producto = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, help_text="Ej: Herbicida, Insecticida")
    
    unidad_medida = models.CharField(max_length=2, choices=UnidadMedida.choices, default=UnidadMedida.LITROS)
    cantidad_ingresada = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)], default=0.0)
    cantidad_usada = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0.0)])
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    ubicaciones = models.ManyToManyField('caracteristicas.Ubicacion', blank=True, related_name="controles_plaga_ubicados")
    proveedores = models.ManyToManyField('caracteristicas.Proveedor', blank=True, related_name='controles_plaga')
    fecha_compra = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(default=datetime.date.today)
    imagen = CloudinaryField('image', folder='control_plagas', null=True, blank=True)
    descripcion = models.TextField(max_length=1000, blank=True, null=True, help_text="Descripción del producto de control de plagas.")

    @property
    def cantidad_restante(self):
        return self.cantidad_ingresada - self.cantidad_usada

    def __str__(self):
        return f"{self.nombre_producto} ({self.cantidad_restante} {self.get_unidad_medida_display()})"

class Potrero(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Potrero La Loma")
    area_hectareas = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Boolean fields for current state
    empastado = models.BooleanField(default=False)
    fumigado = models.BooleanField(default=False)
    rozado = models.BooleanField(default=False)
    
    # Date fields for next actions
    fecha_proximo_empaste = models.DateField(null=True, blank=True)
    fecha_proxima_fumigacion = models.DateField(null=True, blank=True)
    fecha_proximo_rozado = models.DateField(null=True, blank=True)

    # Fields for potrero swap
    intercambio_con_potrero = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='intercambios_programados')
    fecha_intercambio = models.DateField(null=True, blank=True)

    imagen = CloudinaryField('image', folder='potreros', null=True, blank=True)
    descripcion = models.TextField(max_length=1000, blank=True, null=True, help_text="Descripción y estado del potrero.")
    
    def __str__(self): 
        return self.nombre

class Mantenimiento(models.Model):
    equipo = models.CharField(max_length=100, help_text="Ej: Tractor, Guadaña")
    fecha_ultimo_mantenimiento = models.DateField(default=timezone.now)
    fecha_proximo_mantenimiento = models.DateField()
    completado = models.BooleanField(default=False)
    imagen = CloudinaryField('image', folder='mantenimiento', null=True, blank=True)
    descripcion = models.TextField(max_length=1000, blank=True, null=True, help_text="Descripción detallada del mantenimiento realizado o por realizar.")
    def __str__(self): return f"Mantenimiento de {self.equipo} - Próximo: {self.fecha_proximo_mantenimiento}"
    
# acá va la foranea esa de mantenimiento que ud dijo 
    lugares_mantenimiento = models.ManyToManyField(
        'LugarMantenimiento',
        blank=True,
        related_name="mantenimientos"
    )

class Combustible(models.Model):
    tipo = models.CharField(max_length=50, help_text="Ej: Diesel, Gasolina")
    cantidad_galones_ingresada = models.DecimalField("Galones ingresados", max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)], default=0.0)
    cantidad_galones_usados = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0.0)])
    precio = models.DecimalField("Precio por galón", max_digits=10, decimal_places=2, default=0.0)
    ubicaciones = models.ManyToManyField('caracteristicas.Ubicacion', blank=True, related_name="combustibles_ubicados")
    proveedores = models.ManyToManyField('caracteristicas.Proveedor', blank=True, related_name='combustibles')
    imagen = CloudinaryField('image', folder='combustible', null=True, blank=True)
    descripcion = models.TextField(max_length=1000, blank=True, null=True, help_text="Notas sobre el combustible.")

    @property
    def cantidad_galones_restantes(self):
        return self.cantidad_galones_ingresada - self.cantidad_galones_usados

    def __str__(self):
        return f"{self.tipo} - {self.cantidad_galones_restantes} galones restantes"

# tablitas nuevas de aca pa abajo bro :v

class LugarMantenimiento(models.Model):
    nombre_lugar = models.CharField(max_length=150)
    nombre_empresa = models.CharField(max_length=150)
    direccion = models.CharField(max_length=200)
    correo = models.EmailField()
    numero = models.CharField(max_length=20, help_text="Teléfono de contacto")
    ubicaciones = models.ManyToManyField('caracteristicas.Ubicacion', blank=True, related_name="lugares_mantenimiento_ubicados")
    proveedores = models.ManyToManyField('caracteristicas.Proveedor', blank=True, related_name='lugares_mantenimiento')
    descripcion = models.TextField(max_length=1000, blank=True, null=True, help_text="Descripción del lugar de mantenimiento.")

    def __str__(self):
        return f"{self.nombre_lugar} - {self.nombre_empresa}"


class Trabajador(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    correo = models.EmailField()
    numero = models.CharField(max_length=20, help_text="Teléfono de contacto")

    class Meta:
        verbose_name = 'Trabajador'
        verbose_name_plural = 'Trabajadores'

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cedula}"



class Dotacion(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name="dotaciones")
    camisa_franela = models.BooleanField(default=False)
    pantalon = models.BooleanField(default=False)
    zapato = models.BooleanField(default=False)
    fecha_entrega = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = 'Dotación'
        verbose_name_plural = 'Dotaciones'

    def __str__(self):
        return f"Dotación de {self.trabajador}"


class Pago(models.Model):
    class FormaPago(models.TextChoices):
        MENSUAL = 'M', 'Mensual'
        QUINCENAL = 'Q', 'Quincenal'
        SEMANAL = 'S', 'Semanal'

    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name="pagos")
    pago_realizado = models.BooleanField(default=False)
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    metodo_pago = models.CharField(max_length=50, help_text="Ej: Efectivo, Transferencia")
    forma_pago = models.CharField(max_length=1, choices=FormaPago.choices, default=FormaPago.MENSUAL)
    fecha_pago = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Pago a {self.trabajador} - {self.get_forma_pago_display()} - {self.fecha_pago}"


class Comprador(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'Comprador'
        verbose_name_plural = 'Compradores'

    def __str__(self):
        return self.nombre


class VentaProducto(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    comprador = models.ForeignKey('Comprador', on_delete=models.CASCADE)
    valor_compra = models.DecimalField(max_digits=10, decimal_places=2)
    valor_abono = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    
    class Meta:
        verbose_name = 'Venta de Producto'
        verbose_name_plural = 'Ventas de Productos'

    def __str__(self):
        return f"Venta de {self.producto.nombre} a {self.comprador.nombre} por {self.valor_compra}"

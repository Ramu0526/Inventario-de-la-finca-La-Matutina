# inventario/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField
from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta

# --- NUEVOS MODELOS PARA 'INVENTARIO' ---

class Producto(models.Model):
    class UnidadMedida(models.TextChoices):
        UNIDADES = 'U', 'Unidades'
        KILOGRAMOS = 'Kg', 'Kilogramos (Kg)'
        GRAMOS = 'g', 'Gramos (g)'
        LITROS = 'L', 'Litros (L)'
        MILILITROS = 'ml', 'Mililitros (ml)'
    
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey('caracteristicas.Categoria', on_delete=models.SET_NULL, null=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    unidad_medida = models.CharField(max_length=2, choices=UnidadMedida.choices, default=UnidadMedida.UNIDADES)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    proveedor = models.ForeignKey('caracteristicas.Proveedor', on_delete=models.SET_NULL, null=True, blank=True)
    ubicacion = models.ForeignKey('caracteristicas.Ubicacion', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_produccion = models.DateField(default=timezone.now)
    fecha_venta = models.DateField(null=True, blank=True)
    imagen = CloudinaryField('image', folder='productos', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.get_unidad_medida_display()})"
    
class Ganado(models.Model):
    # Opciones para los campos de seleccion
    class RazaAnimal(models.TextChoices):
        VACA = 'VACA', 'Vaca'
        TORO = 'TORO', 'Toro'
        CABALLO = 'CABALLO', 'Caballo'
        YEGUA = 'YEGUA', 'Yegua'
        PERRO = 'PERRO', 'Perro'
        GATO = 'GATO', 'Gato'
        GALLINA = 'GALLINA', 'Gallina'
        GALLO = 'GALLO', 'Gallo'
        PATO = 'PATO', 'Pato'
    
    class GeneroAnimal(models.TextChoices):
        MACHO = 'M', 'Macho'
        HEMBRA = 'H', 'Hembra'

    class EstadoAnimal(models.TextChoices):
        VIVO = 'VIVO', 'Vivo'
        FALLECIDO = 'FALLECIDO', 'Fallecido'
        VENDIDO = 'VENDIDO', 'Vendido'

    class TipoParto(models.TextChoices):
        NATURAL = 'NATURAL', 'Natural'
        INSEMINACION = 'INSEMINACION', 'Inseminación'
        ARTIFICIAL = 'ARTIFICIAL', 'Artificial'
        NO_APLICA = 'NO_APLICA', 'No Aplica'

    # Campos del modelo
    identificador = models.CharField(max_length=50, unique=True, help_text="Ej: Arete N° 123")
    raza = models.CharField(max_length=10, choices=RazaAnimal.choices, default=RazaAnimal.VACA)
    genero = models.CharField(max_length=1, choices=GeneroAnimal.choices, default=GeneroAnimal.HEMBRA)
    potrero = models.ForeignKey('Potrero', on_delete=models.SET_NULL, null=True, blank=True)
    
    fecha_nacimiento = models.DateField()
    fecha_ingreso = models.DateField(default=timezone.now)
    estado = models.CharField(max_length=10, choices=EstadoAnimal.choices, default=EstadoAnimal.VIVO)
    
    # Campos de vacunacion
    vacunado = models.BooleanField(default=False)
    nombre_vacuna = models.CharField(max_length=100, blank=True, null=True)
    proxima_vacunacion = models.DateField(blank=True, null=True)

    # Campo de parto (solo lectura en admin)
    parto = models.CharField(max_length=15, choices=TipoParto.choices, default=TipoParto.NO_APLICA)

    imagen = CloudinaryField('image', folder='ganado', null=True, blank=True)
    
    @property
    def edad(self):
        hoy = datetime.date.today()
        diferencia = relativedelta(hoy, self.fecha_nacimiento)
        return f"{diferencia.years} años, {diferencia.months} meses"

    def __str__(self): 
        return f"{self.identificador} - {self.get_raza_display()}"

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
    ubicacion = models.ForeignKey('caracteristicas.Ubicacion', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_compra = models.DateField(default=timezone.now)
    fecha_ingreso = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    imagen = CloudinaryField('image', folder='medicamentos', null=True, blank=True)
    
    @property
    def cantidad_restante(self):
        return self.cantidad_ingresada - self.cantidad_usada
    
    def __str__(self): 
        return self.nombre

# inventario/models.py

# inventario/models.py

class Alimento(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Heno, Silo de maíz, Sal mineral")
    categoria = models.ForeignKey('caracteristicas.Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    # --- LÍNEA AÑADIDA ---
    etiquetas = models.ManyToManyField('caracteristicas.Etiqueta', blank=True)
    
    cantidad_kg_ingresada = models.DecimalField("Cantidad (Kg)", max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)], default=0.0)
    cantidad_kg_usada = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0.0)])
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    ubicacion = models.ForeignKey('caracteristicas.Ubicacion', on_delete=models.SET_NULL, null=True)
    proveedor = models.ForeignKey('caracteristicas.Proveedor', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_compra = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(default=datetime.date.today)
    imagen = CloudinaryField('image', folder='alimentos', null=True, blank=True)

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
    
    ubicacion = models.ForeignKey('caracteristicas.Ubicacion', on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey('caracteristicas.Proveedor', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_compra = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(default=datetime.date.today)
    imagen = CloudinaryField('image', folder='control_plagas', null=True, blank=True)

    @property
    def cantidad_restante(self):
        return self.cantidad_ingresada - self.cantidad_usada

    def __str__(self):
        return f"{self.nombre_producto} ({self.cantidad_restante} {self.get_unidad_medida_display()})"

class Potrero(models.Model):
    class TamanoPotrero(models.TextChoices):
        PEQUENO = 'P', 'Pequeño'
        MEDIANO = 'M', 'Mediano'
        GRANDE = 'G', 'Grande'

    nombre = models.CharField(max_length=100, help_text="Ej: Potrero La Loma")
    tamano = models.CharField("Tamaño", max_length=1, choices=TamanoPotrero.choices, default=TamanoPotrero.MEDIANO)
    area_hectareas = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = CloudinaryField('image', folder='potreros', null=True, blank=True)
    
    def __str__(self): 
        return f"{self.nombre} ({self.get_tamano_display()})"

class Mantenimiento(models.Model):
    equipo = models.CharField(max_length=100, help_text="Ej: Tractor, Guadaña")
    fecha_ultimo_mantenimiento = models.DateField(default=timezone.now)
    fecha_proximo_mantenimiento = models.DateField()
    completado = models.BooleanField(default=False)
    imagen = CloudinaryField('image', folder='mantenimiento', null=True, blank=True)
    def __str__(self): return f"Mantenimiento de {self.equipo} - Próximo: {self.fecha_proximo_mantenimiento}"

class Combustible(models.Model):
    tipo = models.CharField(max_length=50, help_text="Ej: Diesel, Gasolina")
    cantidad_galones_ingresada = models.DecimalField("Galones ingresados", max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)], default=0.0)
    cantidad_galones_usados = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0.0)])
    precio = models.DecimalField("Precio por galón", max_digits=10, decimal_places=2, default=0.0)
    imagen = CloudinaryField('image', folder='combustible', null=True, blank=True)

    @property
    def cantidad_galones_restantes(self):
        return self.cantidad_galones_ingresada - self.cantidad_galones_usados

    def __str__(self):
        return f"{self.tipo} - {self.cantidad_galones_restantes} galones restantes"
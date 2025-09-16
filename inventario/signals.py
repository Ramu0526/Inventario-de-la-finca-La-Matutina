# inventario/signals.py
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import cloudinary
from .models import (
    Producto, Ganado, Medicamento, Alimento, ControlPlaga,
    Potrero, Mantenimiento, Combustible
)

# Lista de todos los modelos que tienen un campo de imagen
MODELS_WITH_IMAGES = [
    Producto, Ganado, Medicamento, Alimento, ControlPlaga,
    Potrero, Mantenimiento, Combustible
]

@receiver(pre_save)
def handle_image_change(sender, instance, **kwargs):
    """
    Se ejecuta antes de guardar una instancia.
    Borra la imagen antigua si se sube una nueva o si se limpia el campo.
    """
    if sender in MODELS_WITH_IMAGES and instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            old_image = old_instance.imagen
            new_image = instance.imagen

            # Comprueba si el campo de la imagen ha cambiado y si existía una imagen antigua.
            if old_image and old_image != new_image:
                # Borra la imagen antigua de Cloudinary
                cloudinary.uploader.destroy(old_image.public_id)
        except sender.DoesNotExist:
            # Si el objeto es nuevo, no hay nada que hacer.
            pass

@receiver(post_delete)
def handle_image_delete_on_model_delete(sender, instance, **kwargs):
    """
    Se ejecuta después de que un objeto es eliminado.
    Borra la imagen asociada de Cloudinary.
    """
    if sender in MODELS_WITH_IMAGES:
        if instance.imagen:
            # Borra la imagen de Cloudinary
            cloudinary.uploader.destroy(instance.imagen.public_id)
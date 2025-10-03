# inventario/management/commands/enviar_recordatorios.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from inventario.models import Alimento, Medicamento, Vacuna, Mantenimiento, Pago
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class Command(BaseCommand):
    help = 'Envía recordatorios por correo electrónico para fechas de vencimiento próximas.'

    def handle(self, *args, **options):
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=7)

        try:
            superusuario = User.objects.filter(is_superuser=True).first()
            if not superusuario or not superusuario.email:
                self.stdout.write(self.style.ERROR('No se encontró un superusuario con correo electrónico.'))
                return
            destinatario = superusuario.email
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No hay superusuarios configurados.'))
            return

        context = {
            'alimentos': Alimento.objects.filter(fecha_vencimiento__range=[hoy, limite]),
            'medicamentos': Medicamento.objects.filter(fecha_vencimiento__range=[hoy, limite]),
            'vacunas': Vacuna.objects.filter(fecha_vencimiento__range=[hoy, limite]),
            'mantenimientos': Mantenimiento.objects.filter(fecha_proximo_mantenimiento__range=[hoy, limite]),
            'pagos': Pago.objects.filter(fecha_pago__range=[hoy, limite], pago_realizado=False),
        }

        # Comprobar si hay algo que notificar
        hay_recordatorios = any(context.values())

        if hay_recordatorios:
            asunto = 'Recordatorios de Fechas Importantes - Finca La Matutina'
            
            # Renderizar la plantilla HTML
            html_mensaje = render_to_string('inventario/email/recordatorio.html', context)
            
            # Crear una versión de texto plano como alternativa
            texto_plano_mensaje = strip_tags(html_mensaje)

            send_mail(
                asunto,
                texto_plano_mensaje,
                settings.EMAIL_HOST_USER,
                [destinatario],
                html_message=html_mensaje, # Aquí se adjunta el HTML
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Correo de recordatorio enviado a {destinatario}'))
        else:
            self.stdout.write(self.style.SUCCESS('No hay recordatorios para enviar.'))
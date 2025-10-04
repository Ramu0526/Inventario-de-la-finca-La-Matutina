# inventario/management/commands/enviar_recordatorios.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from inventario.models import Alimento, Medicamento, Vacuna, Mantenimiento, Pago, Dotacion
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# --- Constantes ---
DIAS_ANTICIPACION = 7
MESES_DOTACION = 4

class Command(BaseCommand):
    help = 'Envía recordatorios por correo electrónico para fechas de vencimiento y tareas próximas.'

    def _get_superusuario(self):
        """Obtiene el primer superusuario con un correo electrónico configurado."""
        try:
            superusuario = User.objects.filter(is_superuser=True, email__isnull=False).first()
            if not superusuario:
                self.stdout.write(self.style.ERROR('No se encontró un superusuario con correo electrónico.'))
                return None
            return superusuario
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('No hay superusuarios configurados.'))
            return None

    def _get_alimentos_por_vencer(self, hoy, limite):
        return Alimento.objects.filter(fecha_vencimiento__range=[hoy, limite])

    def _get_medicamentos_por_vencer(self, hoy, limite):
        return Medicamento.objects.filter(fecha_vencimiento__range=[hoy, limite])

    def _get_vacunas_por_vencer(self, hoy, limite):
        return Vacuna.objects.filter(fecha_vencimiento__range=[hoy, limite])

    def _get_mantenimientos_proximos(self, hoy, limite):
        return Mantenimiento.objects.filter(fecha_proximo_mantenimiento__range=[hoy, limite], completado=False)

    def _get_pagos_pendientes(self, hoy, limite):
        return Pago.objects.filter(fecha_pago__range=[hoy, limite], pago_realizado=False)

    def _get_dotaciones_proximas(self, hoy, limite):
        """
        Calcula las próximas dotaciones basadas en la última entrega.
        La dotación se entrega cada `MESES_DOTACION` meses.
        """
        dotaciones_proximas = []
        # Obtenemos la dotación más reciente para cada trabajador
        trabajadores_ids = Dotacion.objects.values_list('trabajador_id', flat=True).distinct()
        
        for trabajador_id in trabajadores_ids:
            ultima_dotacion = Dotacion.objects.filter(trabajador_id=trabajador_id).latest('fecha_entrega')
            
            # Calculamos la fecha de la próxima dotación
            fecha_proxima_dotacion = ultima_dotacion.fecha_entrega + relativedelta(months=MESES_DOTACION)

            # Si la próxima fecha está en el rango, la añadimos a la lista
            if hoy <= fecha_proxima_dotacion <= limite:
                # Creamos un objeto "virtual" para pasarlo al template
                dotaciones_proximas.append({
                    'trabajador': ultima_dotacion.trabajador,
                    'fecha_proxima_entrega': fecha_proxima_dotacion
                })
        return dotaciones_proximas

    def handle(self, *args, **options):
        superusuario = self._get_superusuario()
        if not superusuario:
            return

        hoy = timezone.now().date()
        limite = hoy + timedelta(days=DIAS_ANTICIPACION)
        destinatario = superusuario.email

        context = {
            'alimentos': self._get_alimentos_por_vencer(hoy, limite),
            'medicamentos': self._get_medicamentos_por_vencer(hoy, limite),
            'vacunas': self._get_vacunas_por_vencer(hoy, limite),
            'mantenimientos': self._get_mantenimientos_proximos(hoy, limite),
            'pagos': self._get_pagos_pendientes(hoy, limite),
            'dotaciones': self._get_dotaciones_proximas(hoy, limite),
        }

        # Comprobar si hay algo que notificar
        hay_recordatorios = any(context.values())

        if hay_recordatorios:
            asunto = 'Recordatorios de Fechas Importantes - Finca La Matutina'
            
            html_mensaje = render_to_string('inventario/email/recordatorio.html', context)
            texto_plano_mensaje = strip_tags(html_mensaje)

            try:
                send_mail(
                    asunto,
                    texto_plano_mensaje,
                    settings.EMAIL_HOST_USER,
                    [destinatario],
                    html_message=html_mensaje,
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'Correo de recordatorio enviado a {destinatario}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al enviar el correo: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS('No hay recordatorios para enviar.'))
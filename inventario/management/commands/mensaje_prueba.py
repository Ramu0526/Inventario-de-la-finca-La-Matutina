# inventario/management/commands/mensaje_prueba.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class Command(BaseCommand):
    help = 'Envía un correo electrónico de prueba con formato HTML.'

    def handle(self, *args, **options):
        asunto = 'Prueba de Correo desde Finca La Matutina'
        
        # --- CAMBIA ESTA LÍNEA por tu correo personal ---
        destinatario = ['danielmarkc2605@gmail.com'] 

        try:
            self.stdout.write(self.style.NOTICE(f"Enviando correo de prueba a {destinatario[0]}..."))

            # Renderizar la plantilla HTML (no necesita contexto porque es estática)
            html_mensaje = render_to_string('inventario/email/mensaje_prueba.html')
            
            # Crear la versión de texto plano
            texto_plano_mensaje = strip_tags(html_mensaje)

            send_mail(
                asunto,
                texto_plano_mensaje,
                settings.EMAIL_HOST_USER,
                destinatario,
                html_message=html_mensaje,
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('¡Correo de prueba con nuevo formato enviado! Revisa tu bandeja de entrada.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al enviar el correo: {e}'))
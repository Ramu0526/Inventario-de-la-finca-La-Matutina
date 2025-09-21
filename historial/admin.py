# historial/admin.py

from django.contrib import admin
from django.contrib.admin.models import LogEntry
import json

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'readable_change_message', 'action_flag')
    list_filter = ('action_time', 'user', 'content_type')
    search_fields = ('object_repr', 'change_message')

    def readable_change_message(self, obj):
        try:
            message_data = json.loads(obj.change_message)
            
            if 'added' in message_data[0]:
                return "Objeto añadido."
            
            if 'deleted' in message_data[0]:
                return "Objeto eliminado."
                
            if 'changed' in message_data[0]:
                changed_fields = message_data[0]['changed']['fields']
                
                translated_fields = []
                model = obj.content_type.model_class()
                
                for field_name in changed_fields:
                    try:
                        verbose_name = model._meta.get_field(field_name).verbose_name
                        translated_fields.append(str(verbose_name).capitalize())
                    except:
                        translated_fields.append(field_name)

                field_names = ", ".join(translated_fields)
                return f"Se modificaron los campos: {field_names}"

        except (json.JSONDecodeError, IndexError, KeyError, AttributeError):
            return obj.change_message

    readable_change_message.short_description = 'Detalle del Cambio'

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
# historial/admin.py
from django.contrib import admin
from django.contrib.admin.models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'change_message', 'action_flag')
    list_filter = ('action_time', 'user', 'content_type')
    search_fields = ('object_repr', 'change_message')

    # Para que sea de solo lectura
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
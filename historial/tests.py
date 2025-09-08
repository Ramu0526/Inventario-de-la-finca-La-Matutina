# historial/tests.py

from django.test import TestCase, RequestFactory
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth.models import User, ContentType
from .admin import LogEntryAdmin
import json

class LogEntryAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.content_type = ContentType.objects.get_for_model(User)
        self.log_entry_admin = LogEntryAdmin(LogEntry, None)

    def test_readable_change_message_added(self):
        log_entry = LogEntry.objects.create(
            user=self.user,
            content_type=self.content_type,
            object_id='1',
            object_repr='testuser',
            action_flag=ADDITION,
            change_message=json.dumps([{'added': {}}])
        )
        self.assertEqual(self.log_entry_admin.readable_change_message(log_entry), "Objeto añadido.")

    def test_readable_change_message_deleted(self):
        log_entry = LogEntry.objects.create(
            user=self.user,
            content_type=self.content_type,
            object_id='1',
            object_repr='testuser',
            action_flag=DELETION,
            change_message=json.dumps([{'deleted': {}}])
        )
        self.assertEqual(self.log_entry_admin.readable_change_message(log_entry), "Objeto eliminado.")

    def test_readable_change_message_changed_with_verbose_name(self):
        log_entry = LogEntry.objects.create(
            user=self.user,
            content_type=self.content_type,
            object_id='1',
            object_repr='testuser',
            action_flag=CHANGE,
            change_message=json.dumps([{'changed': {'fields': ['first_name']}}])
        )
        self.assertEqual(self.log_entry_admin.readable_change_message(log_entry), "Se modificaron los campos: Nombre")

    def test_readable_change_message_changed_without_verbose_name(self):
        log_entry = LogEntry.objects.create(
            user=self.user,
            content_type=self.content_type,
            object_id='1',
            object_repr='testuser',
            action_flag=CHANGE,
            change_message=json.dumps([{'changed': {'fields': ['some_field_without_verbose_name']}}])
        )
        self.assertEqual(self.log_entry_admin.readable_change_message(log_entry), "Se modificaron los campos: some_field_without_verbose_name")

    def test_readable_change_message_invalid_json(self):
        log_entry = LogEntry.objects.create(
            user=self.user,
            content_type=self.content_type,
            object_id='1',
            object_repr='testuser',
            action_flag=CHANGE,
            change_message='invalid json'
        )
        self.assertEqual(self.log_entry_admin.readable_change_message(log_entry), 'invalid json')

    def test_has_add_permission(self):
        request = self.factory.get('/')
        self.assertFalse(self.log_entry_admin.has_add_permission(request))

    def test_has_change_permission(self):
        request = self.factory.get('/')
        self.assertFalse(self.log_entry_admin.has_change_permission(request))

    def test_has_delete_permission(self):
        request = self.factory.get('/')
        self.assertFalse(self.log_entry_admin.has_delete_permission(request))

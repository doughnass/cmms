from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from .models import WorkOrder


class WorkOrderTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # create a superuser so tests pass permission checks
        self.admin = User.objects.create_superuser(
            username="admin", password="pass", email="admin@example.com"
        )
        self.client = Client()

    def test_create_workorder_requires_login(self):
        resp = self.client.get("/workorders/create")
        self.assertIn(resp.status_code, (302, 301))  # redirect to login

    def test_create_workorder(self):
        self.client.login(username="admin", password="pass")
        resp = self.client.post(
            "/workorders/create", {"title": "Test WO", "description": "desc"}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(WorkOrder.objects.filter(title="Test WO").exists())

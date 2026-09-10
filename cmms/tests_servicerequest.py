from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from cmms.models import ServiceRequest, WorkOrder


class ServiceRequestFlowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            "tester", email="tester@example.local", password="password"
        )
        self.staff = User.objects.create_user(
            "staff", email="staff@example.local", password="password", is_staff=True
        )
        # make staff a superuser so permission_required checks in views pass in tests
        self.staff.is_superuser = True
        self.staff.save()
        self.client = Client()

    def test_create_sr_and_list(self):
        # create SR via view
        resp = self.client.post(
            "/service-request/create",
            {
                "title": "Test SR",
                "description": "desc",
                "customer_name": "C",
                "customer_email": "c@example.local",
            },
        )
        self.assertEqual(resp.status_code, 302)  # redirect to index
        sr = ServiceRequest.objects.filter(title="Test SR").first()
        self.assertIsNotNone(sr)

    def test_prefill_workorder_from_sr(self):
        sr = ServiceRequest.objects.create(
            title="Prefill SR", description="prefill desc"
        )
        # login as staff to access view
        self.client.login(username="staff", password="password")
        resp = self.client.get(f"/workorders/create?from_sr={sr.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "กำลังสร้างใบงานจากคำขอรับบริการ")
        self.assertContains(resp, sr.title)

    def test_quick_convert_creates_wo_and_logs(self):
        sr = ServiceRequest.objects.create(title="Convert SR", description="to convert")
        self.client.login(username="staff", password="password")
        resp = self.client.post(
            f"/service-requests/{sr.id}",
            {"action": "convert_to_wo", "convert_note": "urgent"},
        )
        # should redirect to workorder_detail
        self.assertEqual(resp.status_code, 302)
        sr.refresh_from_db()
        self.assertEqual(sr.status, "converted")
        self.assertIsNotNone(sr.converted_to)
        wo = WorkOrder.objects.get(id=sr.converted_to.id)
        self.assertIn("From SR", wo.logs.first().note)

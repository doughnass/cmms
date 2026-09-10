from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from cmms.models import MasterItem


class Select2SkillsAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        user = get_user_model().objects.create_user(
            username="select2_tester", password="testpass123"
        )
        self.client.force_login(user)

    def test_select2_skills_returns_only_technician_skill_category(self):
        # create some MasterItem rows
        m1 = MasterItem.objects.create(
            category="technician_skill", code="vent", label="Ventilator", active=True
        )
        m2 = MasterItem.objects.create(
            category="technician_skill", code="xray", label="X-Ray", active=True
        )
        # different category should not be returned
        m3 = MasterItem.objects.create(
            category="equipment_type", code="vent", label="Ventilator Type", active=True
        )

        url = reverse("api_select2_skills")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        results = data.get("results")
        # expect 2 results (m1,m2) and each must have id and text
        ids = {r.get("id") for r in results}
        texts = {r.get("text") for r in results}
        self.assertIn(m1.id, ids)
        self.assertIn(m2.id, ids)
        self.assertNotIn(m3.id, ids)
        self.assertIn("Ventilator", texts)
        self.assertIn("X-Ray", texts)

    def test_select2_skills_search_query_filters_labels(self):
        MasterItem.objects.create(
            category="technician_skill", code="vent", label="Ventilator", active=True
        )
        MasterItem.objects.create(
            category="technician_skill", code="pump", label="Suction Pump", active=True
        )
        url = reverse("api_select2_skills")
        resp = self.client.get(url, {"q": "pump"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        results = data.get("results")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("text"), "Suction Pump")

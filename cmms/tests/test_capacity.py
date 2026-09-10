
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from cmms.models import (Equipment_list, MaintenanceAppointment,
                         MaintenanceCapacity, Technician,
                         TechnicianAvailability)


class CapacityAndTechnicianAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.today = timezone.localtime().date()
        user = get_user_model().objects.create_user(
            username="capacity_tester", password="testpass123"
        )
        self.client.force_login(user)

    def _make_equipment(self, equipment_type):
        # create minimal Equipment_list required fields
        return Equipment_list.objects.create(
            equipment_id=f"TEST-{equipment_type}-1",
            equipment_code=f"CODE-{equipment_type}",
            equipment_name_EN=f"EN {equipment_type}",
            equipment_name_TH=f"TH {equipment_type}",
            equipment_brand="Brand",
            equipment_model="Model",
            equipment_sn="SN123",
            equipment_gov="GOV1",
            equipment_price=100,
            equipment_photo="",
            equipment_type=equipment_type,
            equipment_life=10,
            equipment_waranty_date=self.today,
            equipment_waranty_due=self.today,
            equipment_distributor_name="D",
            equipment_distributor_tel="T",
            equipment_sv_subunit="S",
            equipment_sv_unit="U",
            equipment_sv_department="Dept",
            equipment_pm_fq=12,
            equipment_pm_date=self.today,
            equipment_pm_due=self.today,
            equipment_cal_fq=0,
            equipment_cal_date=self.today,
            equipment_cal_due=self.today,
            requires_pm=True,
            requires_cal=False,
            equipment_owner_unit="O",
            equipment_owner_section="OS",
            equipment_owner_department="OD",
            equipment_owner_semi_department="",
            equipment_owner_division="DIV",
            equipment_owner_customer="CUST",
            equipment_user_unit="UU",
            equipment_user_section="US",
            equipment_user_semi_department="",
            equipment_user_department="UD",
            equipment_user_division="UDIV",
            equipment_user_customer="UC",
            equipment_register_username="reg",
            equipment_register_adminname="admin",
            equipment_note="",
        )

    def test_api_technicians_by_date_happy_path(self):
        # create technicians and availability
        from cmms.models import MasterItem

        m1 = MasterItem.objects.create(
            category="technician_skill", code="vent", label="ventilator", active=True
        )
        m2 = MasterItem.objects.create(
            category="technician_skill", code="xray", label="xray", active=True
        )
        tech1 = Technician.objects.create(
            name="Tech One", phone="111", per_day_capacity=1, active=True
        )
        tech1.skills_m.add(m1)
        tech2 = Technician.objects.create(
            name="Tech Two", phone="222", per_day_capacity=1, active=True
        )
        tech2.skills_m.add(m2)
        # tech1 working on today, tech2 off
        TechnicianAvailability.objects.create(
            technician=tech1, date=self.today, status="working"
        )
        TechnicianAvailability.objects.create(
            technician=tech2, date=self.today, status="off"
        )

        url = reverse("api_technicians_by_date")
        resp = self.client.get(
            url, {"date": self.today.isoformat(), "skill": "ventilator"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("date"), self.today.isoformat())
        techs = data.get("technicians")
        # should include tech1 only for skill ventilator
        self.assertEqual(len(techs), 1)
        t = techs[0]
        self.assertEqual(t["name"], "Tech One")
        self.assertEqual(t["status"], "working")

    def test_api_check_capacity_with_configured_and_used(self):
        # create equipment and capacity
        _ = self._make_equipment("ventilator")
        # set configured capacity 5 for today
        MaintenanceCapacity.objects.create(
            date=self.today, equipment_type="ventilator", capacity=5
        )

        # create one available technician and two existing appointments
        from cmms.models import MasterItem

        mvent = MasterItem.objects.filter(
            category="technician_skill", label__iexact="ventilator"
        ).first() or MasterItem.objects.create(
            category="technician_skill", code="vent", label="ventilator", active=True
        )
        tech = Technician.objects.create(
            name="Solo Tech", phone="999", per_day_capacity=1, active=True
        )
        tech.skills_m.add(mvent)
        # availability: working
        TechnicianAvailability.objects.create(
            technician=tech, date=self.today, status="working"
        )

        # create two existing appointments for that equipment type on this date
        # create two equipment entries to attribute appointments to
        e1 = self._make_equipment("ventilator")
        e2 = self._make_equipment("ventilator")
        MaintenanceAppointment.objects.create(equipment=e1, scheduled_date=self.today)
        MaintenanceAppointment.objects.create(equipment=e2, scheduled_date=self.today)

        url = reverse("api_check_capacity")
        resp = self.client.get(
            url, {"date": self.today.isoformat(), "equipment_type": "ventilator"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # configured capacity
        self.assertEqual(data.get("capacity_configured"), 5)
        # used should be 2
        self.assertEqual(data.get("used"), 2)
        # available technicians should be 1
        self.assertEqual(data.get("available_techs"), 1)
        # per_tech_capacity default 1
        self.assertEqual(data.get("per_tech_capacity"), 1)
        # estimated capacity = min(configured, available*per_tech_capacity) = min(5,1)=1
        self.assertEqual(data.get("estimated_capacity"), 1)
        # remaining = max(estimated - used, 0) => max(1-2,0)=0
        self.assertEqual(data.get("remaining"), 0)

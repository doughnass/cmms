"""
Tests for dynamic Master Data schema (MasterCategory + MasterFieldDefinition + MasterItem.meta)
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from cmms.models import MasterCategory, MasterFieldDefinition, MasterItem

User = get_user_model()


class DynamicMasterSchemaTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a test user (staff) for admin operations
        self.user = User.objects.create_user(
            username="testadmin", password="testpass", is_staff=True
        )
        self.client.login(username="testadmin", password="testpass")

        # Create a test category with field definitions
        self.category = MasterCategory.objects.create(
            key="test_locations",
            label="Test Locations",
            description="Test category for locations",
        )

        # Create field definitions
        self.field_floor = MasterFieldDefinition.objects.create(
            category=self.category,
            name="floor",
            label="Floor Number",
            field_type="integer",
            required=True,
            order=1,
            help_text="Which floor is this location on?",
        )

        self.field_capacity = MasterFieldDefinition.objects.create(
            category=self.category,
            name="capacity",
            label="Capacity",
            field_type="integer",
            required=False,
            order=2,
            help_text="How many people can this location hold?",
        )

        self.field_has_ac = MasterFieldDefinition.objects.create(
            category=self.category,
            name="has_ac",
            label="Has Air Conditioning",
            field_type="boolean",
            required=False,
            order=3,
        )

    def test_create_category_and_fields(self):
        """Test that category and fields are created correctly"""
        self.assertEqual(self.category.key, "test_locations")
        self.assertEqual(self.category.fields.count(), 3)

        # Check field definitions
        floor_field = self.category.fields.get(name="floor")
        self.assertEqual(floor_field.field_type, "integer")
        self.assertTrue(floor_field.required)

    def test_create_item_with_meta(self):
        """Test creating a MasterItem with meta values"""
        item = MasterItem.objects.create(
            category="test_locations",
            code="room301",
            label="Room 301",
            description="Test room",
            meta={"floor": 3, "capacity": 30, "has_ac": True},
        )

        self.assertEqual(item.meta["floor"], 3)
        self.assertEqual(item.meta["capacity"], 30)
        self.assertTrue(item.meta["has_ac"])

    def test_create_item_via_form_valid(self):
        """Test creating item via POST with valid meta fields"""
        response = self.client.post(
            "/master/add/",
            {
                "category": "test_locations",
                "code": "room401",
                "label": "Room 401",
                "description": "Test room on 4th floor",
                "active": "on",
                "order": "0",
                "meta.floor": "4",
                "meta.capacity": "25",
                "meta.has_ac": "1",
            },
        )

        # Should redirect on success
        self.assertEqual(response.status_code, 302)

        # Check item was created with meta
        item = MasterItem.objects.get(code="room401", category="test_locations")
        self.assertEqual(item.meta["floor"], 4)
        self.assertEqual(item.meta["capacity"], 25)
        self.assertTrue(item.meta["has_ac"])

    def test_create_item_via_form_missing_required(self):
        """Test that missing required meta field returns error"""
        response = self.client.post(
            "/master/add/",
            {
                "category": "test_locations",
                "code": "room501",
                "label": "Room 501",
                "description": "Test room missing floor",
                "active": "on",
                "order": "0",
                # 'meta.floor' is required but missing
                "meta.capacity": "20",
            },
        )

        # Should re-render form with errors (status 200)
        self.assertEqual(response.status_code, 200)
        self.assertIn("meta_errors", response.context)
        self.assertIn("floor", response.context["meta_errors"])

    def test_create_item_via_form_invalid_type(self):
        """Test that invalid type coercion returns error"""
        response = self.client.post(
            "/master/add/",
            {
                "category": "test_locations",
                "code": "room601",
                "label": "Room 601",
                "description": "Test room with invalid floor",
                "active": "on",
                "order": "0",
                "meta.floor": "abc",  # invalid integer
                "meta.capacity": "30",
            },
        )

        # Should re-render with errors
        self.assertEqual(response.status_code, 200)
        self.assertIn("meta_errors", response.context)
        self.assertIn("floor", response.context["meta_errors"])

    def test_edit_item_with_meta(self):
        """Test editing an item with meta"""
        # Create item first
        item = MasterItem.objects.create(
            category="test_locations",
            code="room701",
            label="Room 701",
            meta={"floor": 7, "capacity": 40},
        )

        # Edit via POST
        response = self.client.post(
            f"/master/{item.id}/edit/",
            {
                "category": "test_locations",
                "code": "room701",
                "label": "Room 701 Updated",
                "description": "Updated description",
                "active": "on",
                "order": "0",
                "meta.floor": "8",  # change floor
                "meta.capacity": "50",  # change capacity
                "meta.has_ac": "1",  # add new field
            },
        )

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Check updated meta
        item.refresh_from_db()
        self.assertEqual(item.label, "Room 701 Updated")
        self.assertEqual(item.meta["floor"], 8)
        self.assertEqual(item.meta["capacity"], 50)
        self.assertTrue(item.meta["has_ac"])

    def test_backward_compatibility_no_schema(self):
        """Test that items without schema (old categories) still work"""
        # Create item in a category without schema
        item = MasterItem.objects.create(
            category="old_category",
            code="old001",
            label="Old Item",
            description="Item in category without schema",
        )

        # GET edit form should work
        response = self.client.get(f"/master/{item.id}/edit/")
        self.assertEqual(response.status_code, 200)
        # Should not have field_defs or should be empty
        field_defs = response.context.get("field_defs", [])
        self.assertEqual(len(field_defs), 0)

        # POST should work (just base fields)
        response = self.client.post(
            f"/master/{item.id}/edit/",
            {
                "category": "old_category",
                "code": "old001",
                "label": "Old Item Updated",
                "description": "Updated",
                "active": "on",
                "order": "0",
            },
        )
        self.assertEqual(response.status_code, 302)

        item.refresh_from_db()
        self.assertEqual(item.label, "Old Item Updated")

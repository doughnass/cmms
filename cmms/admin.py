from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from cmms.models import (ChecklistTemplate, ChecklistTemplateItem,
                         Customer_list, Equipment_list, Holiday,
                         MaintenanceAppointment, MaintenanceCapacity,
                         MasterCategory, MasterFieldDefinition, MasterItem,
                         Profile, SparePart,
                         ServiceRequest, ServiceRequestAttachment,
                         ServiceRequestLog, Technician, TechnicianAvailability,
                         WorkOrder, WorkOrderAttachment, WorkOrderComment,
                         WorkOrderChecklist, WorkOrderChecklistResult,
                         WorkOrderLog)


@admin.register(MasterItem)
class MasterItemAdmin(admin.ModelAdmin):
    list_display = ("category", "code", "label", "parent", "active", "order")
    list_filter = ("category", "active")
    search_fields = ("label", "code")


class MasterFieldDefinitionInline(admin.TabularInline):
    model = MasterFieldDefinition
    extra = 1
    fields = (
        "name",
        "label",
        "field_type",
        "required",
        "order",
        "help_text",
        "visible_in_preview",
    )
    ordering = ("order", "name")


@admin.register(MasterCategory)
class MasterCategoryAdmin(admin.ModelAdmin):
    list_display = ("key", "label", "created_at", "updated_at")
    search_fields = ("key", "label")
    inlines = [MasterFieldDefinitionInline]
    fieldsets = (
        ("Basic Info", {"fields": ("key", "label", "description")}),
        (
            "Display Options",
            {
                "fields": ("display_template",),
                "classes": ("collapse",),
                "description": "Django template snippet for custom display labels. Context: label, code, meta.",
            },
        ),
    )


@admin.register(MasterFieldDefinition)
class MasterFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "name",
        "label",
        "field_type",
        "required",
        "order",
        "visible_in_preview",
    )
    list_filter = ("category", "field_type", "required")
    search_fields = ("name", "label")
    ordering = ("category", "order", "name")


@admin.register(Equipment_list)
class EquipmentListAdmin(admin.ModelAdmin):
    """Admin for Equipment_list tailored to match the front-end equipment form.

    This limits the fields shown in admin Add/Edit, provides sensible
    search_fields/list_filters, and keeps registration date read-only.
    """
    list_display = (
        "equipment_id",
        "equipment_name_EN",
        "equipment_brand",
        "equipment_model",
        "equipment_sn",
        "equipment_gov",
        "equipment_user_customer",
    )
    search_fields = (
        "equipment_id",
        "equipment_code",
        "equipment_name_EN",
        "equipment_name_TH",
        "equipment_brand",
        "equipment_model",
        "equipment_sn",
        "equipment_gov",
    )
    list_filter = ("equipment_type", "requires_pm", "requires_cal")
    readonly_fields = ("equipment_register_date",)
    ordering = ("equipment_id",)

    fieldsets = (
        ("Identification", {"fields": ("equipment_id", "equipment_code")} ),
        (
            "Basic info",
            {
                "fields": (
                    "equipment_name_EN",
                    "equipment_name_TH",
                    "equipment_brand",
                    "equipment_model",
                    "equipment_sn",
                    "equipment_gov",
                    "equipment_price",
                    "equipment_photo",
                    "equipment_type",
                    "equipment_life",
                )
            },
        ),
        (
            "Warranty",
            {
                "fields": (
                    "equipment_waranty_date",
                    "equipment_waranty_due",
                    "equipment_distributor_name",
                    "equipment_distributor_tel",
                )
            },
        ),
        (
            "Maintenance / Calibration",
            {
                "fields": (
                    "equipment_pm_fq",
                    "equipment_pm_due",
                    "equipment_cal_fq",
                    "equipment_cal_due",
                    "requires_pm",
                    "requires_cal",
                )
            },
        ),
        (
            "Owner / User",
            {
                "fields": (
                    "equipment_owner_customer",
                    "equipment_user_customer",
                )
            },
        ),
        (
            "Registration",
            {
                "fields": (
                    "equipment_register_username",
                    "equipment_register_adminname",
                    "equipment_register_date",
                    "equipment_note",
                )
            },
        ),
    )
admin.site.register(Customer_list)
admin.site.register(WorkOrder)
admin.site.register(WorkOrderLog)
admin.site.register(WorkOrderComment)
admin.site.register(WorkOrderAttachment)
admin.site.register(WorkOrderChecklist)
admin.site.register(WorkOrderChecklistResult)


class ChecklistTemplateItemInline(admin.TabularInline):
    model = ChecklistTemplateItem
    extra = 1


@admin.register(ChecklistTemplate)
class ChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "workorder_type", "equipment_type", "active", "updated_at")
    list_filter = ("workorder_type", "active")
    search_fields = ("name", "equipment_type")
    inlines = [ChecklistTemplateItemInline]

# Register ServiceRequest models for officer admin
admin.site.register(ServiceRequest)
admin.site.register(ServiceRequestLog)
admin.site.register(ServiceRequestAttachment)


# Register EquipmentHistory for audit trail viewing
from .models import EquipmentHistory

@admin.register(EquipmentHistory)
class EquipmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('equipment_id', 'action_type', 'action_by', 'action_at', 'ip_address')
    list_filter = ('action_type', 'action_at')
    search_fields = ('equipment_id', 'action_by')
    readonly_fields = ('equipment_id', 'action_type', 'action_by', 'action_at', 
                       'ip_address', 'changed_fields', 'old_values', 'new_values', 'notes')
    ordering = ('-action_at',)
    
    def has_add_permission(self, request):
        # History records should only be created programmatically
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of audit records
        return False


@admin.register(MaintenanceCapacity)
class MaintenanceCapacityAdmin(admin.ModelAdmin):
    list_display = ("date", "equipment_type", "capacity")
    list_filter = ("date", "equipment_type")
    search_fields = ("equipment_type",)


@admin.register(MaintenanceAppointment)
class MaintenanceAppointmentAdmin(admin.ModelAdmin):
    list_display = ("equipment", "scheduled_date", "created_by", "created_at")
    list_filter = ("scheduled_date", "equipment__equipment_type")
    search_fields = ("equipment__equipment_id", "equipment__equipment_name_TH")


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "phone", "active")
    # search by name and related MasterItem label for skills
    search_fields = (
        "name",
        "skills_m__label",
    )


@admin.register(TechnicianAvailability)
class TechnicianAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("technician", "date", "status", "note")
    list_filter = ("date", "status")
    search_fields = ("technician__name", "note")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "telephone", "department", "position", "user_type")
    search_fields = ("user__username", "user__email", "telephone", "department", "position")


@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "quantity", "min_quantity", "unit", "unit_cost", "location", "active")
    list_filter = ("active", "category")
    search_fields = ("code", "name", "supplier", "location")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("ข้อมูลอะไหล่", {"fields": ("code", "name", "description", "category", "unit")}),
        ("สต็อก", {"fields": ("quantity", "min_quantity", "unit_cost", "location")}),
        ("ผู้จำหน่าย", {"fields": ("supplier",)}),
        ("อื่นๆ", {"fields": ("compatible_equipment", "active", "notes", "created_at", "updated_at")}),
    )


# Attach Profile as an inline on the built-in User admin so profile fields
# appear on the user change page (admin/auth/user/<id>/change/)
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('telephone', 'department', 'position', 'user_type')
    extra = 0


try:
    admin.site.unregister(User)
except Exception:
    # If User isn't registered yet, ignore
    pass


class CustomUserAdmin(DjangoUserAdmin):
    inlines = (ProfileInline,)


admin.site.register(User, CustomUserAdmin)


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("date", "name", "description", "is_active", "created_at")
    list_filter = ("is_active", "date")
    search_fields = ("name", "description")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at", "created_by")

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by when creating
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

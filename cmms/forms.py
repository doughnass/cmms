
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class ThaiAuthenticationForm(AuthenticationForm):
    """Login form with Thai error messages for pending/rejected registrations.

    Django's ModelBackend refuses to authenticate inactive users, so
    confirm_login_allowed() never runs for them by default. We only look up
    an inactive user for a clearer message after confirming the *correct*
    password was supplied, so wrong-password attempts still get the generic
    error and can't be used to enumerate account status.
    """

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                self.user_cache = self._get_inactive_user_if_password_matches(
                    username, password
                )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def _get_inactive_user_if_password_matches(self, username, password):
        User = get_user_model()
        try:
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:
            return None
        if user.is_active or not user.check_password(password):
            return None
        return user

    def confirm_login_allowed(self, user):
        if user.is_active:
            return
        profile = getattr(user, "profile", None)
        status = getattr(profile, "approval_status", None)
        if status == "pending":
            raise ValidationError(
                "บัญชีของคุณอยู่ระหว่างการตรวจสอบ กรุณารอการอนุมัติจากผู้ดูแลระบบ",
                code="account_pending",
            )
        if status == "rejected":
            reason = (getattr(profile, "rejection_reason", "") or "").strip()
            msg = "คำขอสมัครบัญชีของคุณถูกปฏิเสธ"
            if reason:
                msg += f" (เหตุผล: {reason})"
            raise ValidationError(msg, code="account_rejected")
        raise ValidationError(
            "บัญชีนี้ถูกระงับการใช้งาน กรุณาติดต่อผู้ดูแลระบบ",
            code="inactive",
        )


class WorkOrderForm(forms.ModelForm):
    class Meta:
        from .models import WorkOrder

        model = WorkOrder
        fields = (
            "title",
            "description",
            "equipment",
            "assigned_to",
            "priority",
            "workorder_types",
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "minlength": 5,
                    "placeholder": "เช่น: ซ่อม MEDCMU-000123 - ปุ่มไม่ทำงาน",
                    "id": "id_title",
                    "autocomplete": "off",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "minlength": 1,
                    "id": "id_description",
                    "autocomplete": "off",
                }
            ),
            # use native selects to avoid Select2 overlay issues; JS will still provide a modal chooser if needed
            "equipment": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_equipment",
                    "data-ajax-url": "/api/search/equipment",
                    "data-placeholder": "ค้นหาอุปกรณ์",
                    "autocomplete": "off",
                }
            ),
            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_assigned_to",
                    "data-ajax-url": "/api/search/users",
                    "data-placeholder": "ค้นหาผู้ใช้งาน/ผู้รับผิดชอบ",
                    "autocomplete": "off",
                }
            ),
            "priority": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_priority",
                    "autocomplete": "off",
                }
            ),
            # render workorder_types as a native multiple select (no Select2) to avoid overlapping UI
            "workorder_types": forms.Select(
                attrs={
                    "class": "form-select",
                    "multiple": "multiple",
                    "size": "5",
                    "id": "id_workorder_types",
                    "autocomplete": "off",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # help text to clarify difference between title and types
        self.fields["title"].help_text = (
            'หัวข้อสั้น ๆ สรุปสิ่งที่ต้องการให้ช่างทำ (รวมคำกระทำและรหัสอุปกรณ์ เช่น "ซ่อม MEDCMU-000123 - ปุ่มไม่ทำงาน").'
        )
        # populate choices for workorder_types from MasterItem category
        from .models import MasterItem

        qs = MasterItem.objects.filter(category="workorder_type", active=True).order_by(
            "order", "label"
        )
        # use native select multiple (no Select2) to avoid client-side overlap issues
        self.fields["workorder_types"] = forms.ModelMultipleChoiceField(
            queryset=qs,
            required=False,
            widget=forms.SelectMultiple(attrs={"class": "form-select", "size": "5"}),
        )

    def clean_title(self):
        t = self.cleaned_data.get("title", "")
        if len(t.strip()) < 5:
            raise forms.ValidationError("หัวข้อสั้นเกินไป (อย่างน้อย 5 ตัวอักษร)")
        return t

    def clean_description(self):
        d = self.cleaned_data.get("description", "")
        if len(d.strip()) < 1:
            raise forms.ValidationError("กรุณากรอกรายละเอียด")
        return d


class ServiceRequestForm(forms.ModelForm):
    # Override equipment field to accept text input instead of ForeignKey
    equipment_code = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "id_equipment",
            "autocomplete": "off",
        })
    )
    
    class Meta:
        from .models import ServiceRequest

        model = ServiceRequest
        fields = (
            "title",
            "description",
            "customer_name",
            "customer_email",
            "customer_position",
            "customer_telephone",
            "customer_department",
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control form-control-enhanced",
                    "placeholder": "หัวข้อคำขอ เช่น: ซ่อม MEDCMU-000123",
                    "id": "id_sr_title",
                    "autocomplete": "off",
                    "required": False,  # Remove HTML required attribute since we handle validation in JS
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "id": "id_sr_description",
                    "autocomplete": "off",
                }
            ),
            "customer_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "id_customer_name",
                    "autocomplete": "name",
                }
            ),
            "customer_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "id": "id_customer_email",
                    "autocomplete": "email",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make title field not required since we handle validation in JavaScript
        self.fields['title'].required = False
    
    def save(self, commit=True):
        """Custom save to handle equipment_code"""
        instance = super().save(commit=False)
        
        # Try to find equipment by code
        equipment_code = self.cleaned_data.get('equipment_code', '').strip()
        if equipment_code and equipment_code != 'ไม่มีรหัส':
            from .models import Equipment_list
            try:
                # Support both business ID and legacy code inputs
                equipment = (
                    Equipment_list.objects.filter(equipment_id=equipment_code).first()
                    or Equipment_list.objects.filter(equipment_code=equipment_code).first()
                )
                instance.equipment = equipment
            except Exception:
                # If not found, leave equipment as None
                instance.equipment = None
        else:
            instance.equipment = None
        
        if commit:
            instance.save()
        return instance

    # Note: do not create a separate customer_phone field here — use profile.telephone in templates

    def clean_title(self):
        t = self.cleaned_data.get("title", "").strip()
        if not t:
            raise forms.ValidationError("กรุณาเลือกประเภทงานอย่างน้อย 1 ประเภท")
        if len(t) < 5:
            raise forms.ValidationError("หัวข้อสั้นเกินไป (อย่างน้อย 5 ตัวอักษร)")
        return t



class ProfileForm(forms.ModelForm):
    # extra profile fields stored in Profile (one-to-one)
    telephone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "id": "id_telephone", "autocomplete": "tel"}),
    )
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "id": "id_department", "autocomplete": "off"}),
    )
    position = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "id": "id_position", "autocomplete": "off"}),
    )
    user_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "id": "id_user_type", "autocomplete": "off"}),
    )

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "id_first_name",
                    "autocomplete": "given-name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "id_last_name",
                    "autocomplete": "family-name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "id": "id_email",
                    "autocomplete": "email",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        # instance is the User instance
        super().__init__(*args, **kwargs)
        # populate initial values for profile fields if profile exists
        user = kwargs.get("instance")
        if user is not None:
            try:
                profile = user.profile
            except Exception:
                profile = None
            if profile:
                self.fields["telephone"].initial = profile.telephone
                self.fields["department"].initial = profile.department
                self.fields["position"].initial = profile.position
                self.fields["user_type"].initial = profile.user_type

    def save(self, commit=True):
        # save user fields then profile fields
        user = super().save(commit=commit)
        from .models import Profile

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.telephone = self.cleaned_data.get("telephone", "")
        profile.department = self.cleaned_data.get("department", "")
        profile.position = self.cleaned_data.get("position", "")
        profile.user_type = self.cleaned_data.get("user_type", "")
        if commit:
            profile.save()
        return user

class TechnicianForm(forms.ModelForm):
    class Meta:
        from .models import Technician

        model = Technician
        fields = (
            "prefix_name",
            "prefix_name_custom",
            "user",
            "name",
            "skills_m",
            "phone",
            "per_day_capacity",
            "can_work_shifts",
            "active",
        )
        widgets = {
            "prefix_name": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_prefix_name",
                    "name": "prefix_name",
                    "autocomplete": "honorific-prefix",
                }
            ),

            "prefix_name_custom": forms.TextInput(
                attrs={
                    "id": "id_prefix_name_custom",
                    "name": "prefix_name_custom",
                    "placeholder": "เช่น ศ., รศ., ผศ., ดร., พ.อ.",
                    "autocomplete": "off",
                }
            ),
            "user": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_user",
                    "name": "user",
                    "autocomplete": "off",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "id_name",
                    "name": "name",
                    "autocomplete": "name",
                }
            ),
            # widget left unset here; the ModelMultipleChoiceField and its SelectMultiple
            # widget are configured in __init__ so we avoid duplication and ensure
            # attributes (aria-describedby, ajax URL) are computed at runtime.
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "id_phone",
                    "name": "phone",
                    "autocomplete": "tel",
                }
            ),
            "per_day_capacity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "id": "id_per_day_capacity",
                    "name": "per_day_capacity",
                    "autocomplete": "off",
                }
            ),
            "can_work_shifts": forms.CheckboxInput(
                attrs={"id": "id_can_work_shifts", "name": "can_work_shifts"}
            ),
            "active": forms.CheckboxInput(attrs={"id": "id_active", "name": "active"}),
            # 'skills_m' widget is set in __init__
            "skills_m": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                    "id": "id_skills_select",
                    "name": "skills_m",
                    "size": "5",
                    "multiple": "multiple",
                    "aria-describedby": "skills-help",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # แสดงป้ายชื่อฟิลด์ 'name' เป็นภาษาไทย (ชื่อ-สกุล)
        self.fields["prefix_name"].label = "คำนำหน้า"
        self.fields["prefix_name_custom"].label = "คำนำหน้า (ระบุเอง)"
        self.fields["user"].label = "Username"
        self.fields["name"].label = "ชื่อ-สกุล"
        self.fields["phone"].label = "เบอร์โทรศัพท์"
        self.fields["per_day_capacity"].label = "ความสามารถในการทำงานต่อวัน (ชั่วโมง)"
        self.fields["can_work_shifts"].label = "สามารถขึ้นเวรได้"
        self.fields["active"].label = "ทำงานปกติ"
        self.fields["skills_m"].label = "ทักษะ / ประเภทอุปกรณ์"

        # ModelMultipleChoiceField backed by MasterItem(category='technician_skill')
        from .models import MasterItem

        # Populate queryset so the template renders a native multiple select
        qs = MasterItem.objects.filter(category="equipments", active=True).order_by(
            "order", "label"
        )

        widget_attrs = {
            "class": "form-select",
            "id": "id_skills_select",
            "name": "skills_m",
            "multiple": "multiple",
            "size": "8",
            "aria-label": "ทักษะ / ประเภทอุปกรณ์",
        }

        self.fields["skills_m"] = forms.ModelMultipleChoiceField(
            queryset=qs,
            required=False,
            widget=forms.SelectMultiple(attrs=widget_attrs),
            label="ทักษะ / ประเภทอุปกรณ์",
        )

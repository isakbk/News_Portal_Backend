from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import EmployeeProfile


class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    extra = 0
    fields = (
        "employee_id",
        "full_name",
        "phone",
        "designation",
        "photo",
        "is_active_employee",
    )
    readonly_fields = ("employee_id",)


class CustomUserAdmin(UserAdmin):
    inlines = [EmployeeProfileInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "full_name",
        "designation",
        "user",
        "is_active_employee",
        "created_at",
    )

    list_filter = (
        "designation",
        "is_active_employee",
        "created_at",
    )

    search_fields = (
        "employee_id",
        "full_name",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "employee_id",
        "created_at",
    )

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

        if is_new:
            # Set the default password to the employee_id for new accounts.
            obj.user.is_staff = False
            obj.user.is_superuser = False
            obj.user.set_password(obj.employee_id)
            obj.user.save(update_fields=["password", "is_staff", "is_superuser"])


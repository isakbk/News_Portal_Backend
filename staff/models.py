from django.db import models
from django.contrib.auth.models import User


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    full_name = models.CharField(max_length=150)

    phone = models.CharField(max_length=20, blank=True)

    designation = models.CharField(
        max_length=100,
        default="News Editor"
    )

    photo = models.ImageField(
        upload_to="employees/photos/",
        blank=True,
        null=True
    )

    is_active_employee = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last_employee = EmployeeProfile.objects.order_by(
                "-id"
            ).first()

            next_number = (
                last_employee.id + 1
                if last_employee
                else 1
            )

            self.employee_id = f"EMP{next_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"
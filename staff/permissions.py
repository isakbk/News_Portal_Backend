from rest_framework.permissions import BasePermission


class IsEmployee(BasePermission):
    message = "Only active employees can access this page."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            profile = request.user.employee_profile
            return profile.is_active_employee and request.user.is_active
        except Exception:
            return False



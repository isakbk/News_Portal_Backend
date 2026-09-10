from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminEmployeeViewSet, AdminLoginView, AdminUserViewSet

router = DefaultRouter()
router.register("employees", AdminEmployeeViewSet, basename="admin-employees")
router.register("users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("", include(router.urls)),
]

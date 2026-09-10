from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    EmployeeRegisterView,
    EmployeeLoginView,
    EmployeeProfileView,
    ChangePasswordView,
    EmployeeNewsViewSet,
)

router = DefaultRouter()
router.register("news", EmployeeNewsViewSet, basename="employee-news")

urlpatterns = [
    path("register/", EmployeeRegisterView.as_view(), name="employee-register"),
    path("login/", EmployeeLoginView.as_view(), name="employee-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", EmployeeProfileView.as_view(), name="employee-profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),

    path("", include(router.urls)),
]
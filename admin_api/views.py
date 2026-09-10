from django.core import signing
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from secrets import compare_digest

from staff.models import EmployeeProfile
from .authentication import CODE_ADMIN_TOKEN_PREFIX, CODE_ADMIN_TOKEN_SALT
from .permissions import IsSuperuser
from .serializers import AdminEmployeeCreateSerializer, AdminEmployeeSerializer, AdminUserSerializer


# This administrator is intentionally code-based and is not stored in Django's User table.
CODE_ADMIN_USERNAME = "bkisak101@gmail.com"
CODE_ADMIN_PASSWORD = "isakadmin"


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("username", "").strip()
        password = request.data.get("password", "")
        if not (
            compare_digest(identifier.lower(), CODE_ADMIN_USERNAME.lower())
            and compare_digest(password, CODE_ADMIN_PASSWORD)
        ):
            return Response({"detail": "Invalid administrator credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        payload = {"username": CODE_ADMIN_USERNAME, "email": CODE_ADMIN_USERNAME}
        access = CODE_ADMIN_TOKEN_PREFIX + signing.dumps(payload, salt=CODE_ADMIN_TOKEN_SALT)
        return Response({
            "access": access,
            "refresh": "",
            "user": {"id": None, **payload, "is_active": True},
        })


class AdminEmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperuser]
    queryset = EmployeeProfile.objects.select_related("user").all().order_by("-created_at")

    def get_serializer_class(self):
        return AdminEmployeeCreateSerializer if self.action == "create" else AdminEmployeeSerializer

    def destroy(self, request, *args, **kwargs):
        self.get_object().user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperuser]
    serializer_class = AdminUserSerializer
    queryset = User.objects.filter(is_superuser=True).order_by("username")

    def destroy(self, request, *args, **kwargs):
        if self.get_object().pk == request.user.pk:
            return Response({"detail": "You cannot delete your own administrator account."}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

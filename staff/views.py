from django.contrib.auth import authenticate

from django.contrib.auth.models import User

from django.db import transaction


from rest_framework import generics, status, viewsets

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.response import Response

from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken


from user.models import News

from user.serializers import NewsSerializer


from .models import EmployeeProfile

from .serializers import (
    EmployeeSerializer,
    EmployeeRegistrationSerializer,
    ChangePasswordSerializer,
)

from .permissions import IsEmployee


class EmployeeRegisterView(generics.CreateAPIView):

    serializer_class = EmployeeRegistrationSerializer

    permission_classes = [AllowAny]

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        profile = serializer.save()

        return Response(
            {
                "message": "Employee registered successfully.",
                "employee_id": profile.employee_id,
                "username": profile.user.username,
                "default_password": profile.employee_id,
            },
            status=status.HTTP_201_CREATED,
        )


class EmployeeLoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get("username")

        password = request.data.get("password")

        if not username or not password:

            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        # Employee IDs (for example EMP0001) are also valid login usernames.
        # Resolve the ID to the linked Django user before checking the password.
        try:
            profile_by_id = EmployeeProfile.objects.select_related("user").get(
                employee_id__iexact=username
            )
        except EmployeeProfile.DoesNotExist:
            profile_by_id = None

        if not user and profile_by_id:
            user = authenticate(
                username=profile_by_id.user.username,
                password=password,
            )

            # Compatibility for accounts created by the previous version,
            # whose initial password was the Django username.
            if (
                not user
                and password.upper() == profile_by_id.employee_id.upper()
                and profile_by_id.user.check_password(profile_by_id.user.username)
            ):
                user = profile_by_id.user

        if not user:

            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:

            return Response(
                {"detail": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:

            profile = user.employee_profile

            if not profile.is_active_employee:

                return Response(
                    {"detail": "This employee account is inactive."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except EmployeeProfile.DoesNotExist:

            return Response(
                {"detail": "Employee profile not found."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        requires_password_change = user.check_password(
            user.username
        ) or user.check_password(profile.employee_id)

        return Response(
            {
                "message": "Login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "requires_password_change": requires_password_change,
                "employee": EmployeeSerializer(
                    profile, context={"request": request}
                ).data,
            }
        )


class EmployeeProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = EmployeeSerializer

    permission_classes = [IsEmployee]

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):

        return self.request.user.employee_profile


class ChangePasswordView(APIView):

    permission_classes = [IsEmployee]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])

        request.user.save()

        return Response({"message": "Password changed successfully."})


class EmployeeNewsViewSet(viewsets.ModelViewSet):

    serializer_class = NewsSerializer

    permission_classes = [IsEmployee]

    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return News.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()



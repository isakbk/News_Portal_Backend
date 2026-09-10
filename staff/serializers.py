from django.contrib.auth.models import User

from rest_framework import serializers


from .models import EmployeeProfile


class EmployeeSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username", read_only=True)

    email = serializers.EmailField(source="user.email", read_only=True)

    photo_url = serializers.SerializerMethodField()

    class Meta:

        model = EmployeeProfile

        fields = [
            "id",
            "employee_id",
            "full_name",
            "phone",
            "designation",
            "photo",
            "photo_url",
            "username",
            "email",
            "is_active_employee",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "employee_id",
            "username",
            "email",
            "created_at",
        ]

    def get_photo_url(self, obj):

        request = self.context.get("request")

        if obj.photo:

            url = obj.photo.url

            return request.build_absolute_uri(url) if request else url

        return None


class EmployeeRegistrationSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=150)

    password = serializers.CharField(
        write_only=True, min_length=8, required=False, allow_null=True
    )

    email = serializers.EmailField()

    full_name = serializers.CharField(max_length=150)

    phone = serializers.CharField(max_length=20, required=False)

    designation = serializers.CharField(max_length=100, required=False)

    photo = serializers.ImageField(required=False, allow_null=True)

    def validate_username(self, value):

        if User.objects.filter(username=value).exists():

            raise serializers.ValidationError("Username already exists.")

        return value

    def create(self, validated_data):

        password = validated_data.pop("password", None)

        photo = validated_data.pop("photo", None)

        user = User.objects.create_user(
            username=validated_data.pop("username"),
            email=validated_data.pop("email"),
            password=password,
            is_staff=False,
            is_superuser=False,
        )

        profile = EmployeeProfile.objects.create(
            user=user, photo=photo, **validated_data
        )

        # New staff members sign in once with their generated employee ID.
        # They are immediately required to replace it from the staff frontend.

        if not password:

            user.set_password(profile.employee_id)

            user.save()

        return profile


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    new_password = serializers.CharField(write_only=True, min_length=8)

    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):

        user = self.context["request"].user

        if attrs["new_password"] != attrs["confirm_password"]:

            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        old_password = attrs.get("old_password")

        # The first-login form intentionally has no old-password field. It is
        # allowed only while the account still uses username as its password.
        if old_password:

            if not user.check_password(old_password):

                raise serializers.ValidationError(
                    {"old_password": "Old password is incorrect."}
                )

        else:
            profile = user.employee_profile
            uses_default_password = user.check_password(
                user.username
            ) or user.check_password(profile.employee_id)

            if not uses_default_password:
                raise serializers.ValidationError(
                    {"old_password": "Current password is required."}
                )

        if attrs["new_password"] == user.username:

            raise serializers.ValidationError(
                {"new_password": "Choose a password different from your username."}
            )

        return attrs

    def validate_old_password(self, value):
        return value



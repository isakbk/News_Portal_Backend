from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework import serializers

from staff.models import EmployeeProfile


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "password", "date_joined"]
        read_only_fields = ["id", "date_joined"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_superuser(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.is_staff = True
        instance.is_superuser = True
        instance.save()
        return instance


class AdminEmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email")
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProfile
        fields = ["id", "employee_id", "full_name", "phone", "designation", "photo", "photo_url", "username", "email", "is_active_employee", "created_at"]
        read_only_fields = ["id", "employee_id", "username", "photo_url", "created_at"]

    def get_photo_url(self, obj):
        request = self.context.get("request")
        if obj.photo:
            return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url
        return None

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if "email" in user_data:
            instance.user.email = user_data["email"]
            instance.user.save(update_fields=["email"])
        return super().update(instance, validated_data)


class AdminEmployeeCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    initial_password = serializers.CharField(read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ["full_name", "email", "phone", "designation", "photo", "initial_password"]

    def create(self, validated_data):
        email = validated_data.pop("email", "")
        base_username = slugify(validated_data["full_name"]).replace("-", "") or "employee"
        username = base_username[:150]
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username[:150 - len(str(suffix))]}{suffix}"
        user = User.objects.create_user(username=username, email=email, password=username, is_staff=False, is_superuser=False)
        profile = EmployeeProfile.objects.create(user=user, **validated_data)
        profile.initial_password = username
        return profile

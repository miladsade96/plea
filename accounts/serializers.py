from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, exceptions
from accounts.models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        max_length=100, required=True, write_only=True
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
        )

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"detail": "Password does not match!"})
        try:
            validate_password(attrs.get("password"))
        except exceptions.ValidationError as errors:
            raise serializers.ValidationError({"detail": list(errors.messages)})
        return super(UserRegistrationSerializer, self).validate(attrs)

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        return CustomUser.objects.create_user(**validated_data)

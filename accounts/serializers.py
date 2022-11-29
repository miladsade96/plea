from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, exceptions
from accounts.models import CustomUser


class PetitionsRelatedField(serializers.RelatedField):
    def to_internal_value(self, data):
        return super(PetitionsRelatedField, self).to_internal_value(data)

    def to_representation(self, value):
        return {
            "id": value.pk,
            "title": value.title,
            "slug": value.slug,
            "goal": value.goal,
            "number_of_signatures": value.num_signatures,
            "relative_url": value.get_relative_api_url(),
        }


class UserInfoSerializer(serializers.ModelSerializer):
    user_petitions = PetitionsRelatedField(
        read_only=True, many=True, source="petitions"
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "created_at",
            "updated_at",
            "user_petitions",
        )
        read_only_fields = (
            "first_name",
            "last_name",
            "email",
            "is_active",
            "created_at",
            "updated_at",
            "user_petitions",
        )

    def create(self, validated_data):
        return super(UserInfoSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(UserInfoSerializer, self).update(instance, validated_data)

    def validate(self, attrs):
        username = attrs.get("username")
        try:
            user = CustomUser.objects.get(username__exact=username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"detail": "Username is invalid!"})
        if user.is_active is False:
            raise serializers.ValidationError(
                {
                    "detail": "User account is not active! "
                    "Please activate your account first."
                }
            )
        attrs["user"] = user
        return super(UserInfoSerializer, self).validate(attrs)


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


class UserActivationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100, required=True)

    def create(self, validated_data):
        return super(UserActivationResendSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(UserActivationResendSerializer, self).update(
            instance, validated_data
        )

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = CustomUser.objects.get(email__iexact=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid email!"})
        if user.is_active is True:
            raise serializers.ValidationError(
                {"detail": "User account is already active!"}
            )
        return super(UserActivationResendSerializer, self).validate(attrs)


class ChangeUserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100, required=True)
    new_password = serializers.CharField(max_length=100, required=True)
    new_password_confirm = serializers.CharField(max_length=100, required=True)

    def create(self, validated_data):
        return super(ChangeUserPasswordSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(ChangeUserPasswordSerializer, self).update(
            instance, validated_data
        )

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password_confirm"):
            raise serializers.ValidationError({"detail": "Password does not match!"})
        try:
            validate_password(attrs.get("new_password"))
        except exceptions.ValidationError as errors:
            raise serializers.ValidationError({"detail": list(errors.messages)})
        return super(ChangeUserPasswordSerializer, self).validate(attrs)


class RequestResetForgottenPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = CustomUser.objects.get(email__iexact=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid email"})
        if user.is_active is False:
            raise serializers.ValidationError(
                {
                    "detail": "User account is not active! "
                    "Please activate your account first."
                }
            )
        attrs["user"] = user
        attrs["full_name"] = f"{user.first_name} {user.last_name}"
        return super(RequestResetForgottenPasswordEmailSerializer, self).validate(attrs)

    def create(self, validated_data):
        return super(RequestResetForgottenPasswordEmailSerializer, self).create(
            validated_data
        )

    def update(self, instance, validated_data):
        return super(RequestResetForgottenPasswordEmailSerializer, self).update(
            instance, validated_data
        )


class ResetForgottenPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=100, required=True)
    new_password_confirm = serializers.CharField(
        max_length=100, required=True, write_only=True
    )

    def create(self, validated_data):
        return super(ResetForgottenPasswordSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(ResetForgottenPasswordSerializer, self).update(
            instance, validated_data
        )

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password_confirm"):
            raise serializers.ValidationError({"detail": "Password does not match!"})
        try:
            validate_password(attrs.get("new_password"))
        except exceptions.ValidationError as errors:
            raise serializers.ValidationError({"detail": list(errors.messages)})
        return super(ResetForgottenPasswordSerializer, self).validate(attrs)

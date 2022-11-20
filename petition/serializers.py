from rest_framework import serializers
from petition.models import Petition, Signature, Reason, Vote


class PetitionListCreateSerializer(serializers.ModelSerializer):
    summary = serializers.CharField(source="get_summary", read_only=True)
    relative_url = serializers.CharField(source="get_relative_api_url", read_only=True)
    absolute_url = serializers.SerializerMethodField(
        method_name="get_absolute_api_url", read_only=True
    )

    class Meta:
        model = Petition
        fields = (
            "title",
            "description",
            "owner",
            "recipient_name",
            "recipient_email",
            "image",
            "slug",
            "goal",
            "is_successful",
            "num_signatures",
            "created",
            "updated",
            "signatures",
            "relative_url",
            "absolute_url",
            "summary",
        )
        read_only_fields = [
            "owner",
            "slug",
            "num_signatures",
            "created",
            "updated",
            "signatures",
            "relative_url",
            "absolute_url",
            "summary",
            "is_successful",
        ]

    def get_absolute_api_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.slug)

    def to_representation(self, instance):
        request = self.context.get("request")
        representation = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("slug"):
            representation.pop("summary", None)
        else:
            representation.pop("description", None)
            representation.pop("signatures", None)
        return representation

    def create(self, validated_data):
        validated_data["owner"] = self.context.get("request").user
        return super(PetitionListCreateSerializer, self).create(validated_data)


class PetitionRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Petition
        fields = (
            "title",
            "description",
            "owner",
            "image",
            "slug",
            "goal",
            "num_signatures",
            "created",
            "updated",
            "signatures",
            "reasons",
        )
        read_only_fields = [
            "owner",
            "num_signatures",
            "created",
            "updated",
            "signatures",
            "reasons",
        ]


class SignatureListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = (
            "petition",
            "first_name",
            "last_name",
            "email",
            "country",
            "city",
            "postal_code",
            "let_me_know",
            "is_anonymous",
            "is_verified",
        )
        read_only_fields = ("is_verified",)


class SignatureVerificationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            signature = Signature.objects.get(email=email)
        except Signature.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "Signature has not been created with given email."}
            )
        if signature.is_verified is True:
            raise serializers.ValidationError(
                {
                    "detail": "Signature is already verified and submitted successfully on the petition."
                }
            )
        attrs["full_name"] = f"{signature.first_name} {signature.last_name}"
        attrs["email"] = signature.email
        return super(SignatureVerificationResendSerializer, self).validate(attrs)

    def create(self, validated_data):
        return super(SignatureVerificationResendSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(SignatureVerificationResendSerializer, self).update(
            instance, validated_data
        )


class ReasonListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reason
        fields = (
            "petition",
            "first_name",
            "last_name",
            "why",
            "likes",
            "dislikes",
            "created",
        )
        read_only_fields = ("likes", "dislikes", "created")


class VoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ("reason", "vote", "created")
        read_only_fields = ("created",)

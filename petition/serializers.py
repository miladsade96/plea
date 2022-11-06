from rest_framework import serializers

from petition.models import Petition


class PetitionListCreateSerializer(serializers.ModelSerializer):
    summary = serializers.CharField(source="get_summary", read_only=True)
    relative_url = serializers.CharField(source="get_relative_api_url", read_only=True)
    absolute_url = serializers.SerializerMethodField(method_name="get_absolute_api_url", read_only=True)

    class Meta:
        model = Petition
        fields = ("title", "description", "owner", "image", "slug", "goal",
                  "num_signatures", "created", "updated", "signatures", "relative_url", "absolute_url", "summary")
        read_only_fields = ["owner", "slug", "num_signatures", "created",
                            "updated", "signatures", "relative_url", "absolute_url", "summary"]

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
        fields = ("title", "description", "owner", "image", "slug", "goal",
                  "num_signatures", "created", "updated", "signatures")
        read_only_fields = ["owner", "num_signatures", "created", "updated",
                            "signatures"]

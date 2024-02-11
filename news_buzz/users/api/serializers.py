from typing import Any
from django.contrib.auth import get_user_model
from rest_framework import serializers

from news_buzz.users.models import Participant, Session, User as UserType


User = get_user_model()


class UserSerializer(serializers.ModelSerializer[UserType]):
    class Meta:
        model = User
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class ParticipantSerializer(serializers.ModelSerializer[Participant]):
    class Meta:
        model = Participant
        fields = ["participant_id", "id"]


class SessionSerializer(serializers.ModelSerializer[Session]):
    participant = serializers.CharField(max_length=255, min_length=10, allow_blank=False, allow_null=False)
    # first_name = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, write_only=True)
    login_website_type = serializers.CharField(max_length=255, allow_blank=False, allow_null=False, write_only=True)

    def validate(self, attrs: Any) -> Any:
        if Participant.objects.filter(participant_id=attrs["participant"]).exists():
            raise serializers.ValidationError({"participant": "Participant has already visited before."})
        participant = Participant.objects.create(
            participant_id=attrs.pop("participant"),
            # first_name=attrs.pop("first_name"),
            login_website_type=attrs.pop("login_website_type"),
        )
        attrs["participant"] = participant
        return super().validate(attrs)

    class Meta:
        model = Session
        fields = ["participant", "id", "participant_id", "login_website_type"]

from django.contrib.auth import get_user_model
from rest_framework import serializers

from news_buzz.users.models import Participant,Session, User as UserType


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
    
    class Meta:
        model = Session
        fields = ["participant", "id"]


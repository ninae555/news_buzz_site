from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.utils import timezone
from .serializers import UserSerializer, ParticipantSerializer, SessionSerializer
from news_buzz.users.models import Participant, Session
User = get_user_model()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class ParticipantViewSet(RetrieveModelMixin, GenericViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = ParticipantSerializer
    queryset = Participant.objects.filter(is_active=True)
    lookup_field = "participant_id"

    @action(detail=False, methods=["POST"])
    def login(self, request):
        serializer = SessionSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # deactivate other active session
        Session.objects.filter(participant_id=request.data["participant"], is_active=True).update(is_active=False, end_time=timezone.now())
        serializer.save()
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)

from rest_framework import permissions
from news_buzz.users.models import Session
from uuid import UUID

class IsValidParticipantSession(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.headers.get("session"):
            try:
                UUID(request.headers.get("session"), version=4)
            except ValueError:
                return False
            request.participant_session = Session.objects.filter(
                id=request.headers.get("session"), is_active=True
            ).first()
            return (
                request.participant_session
                and request.participant_session.participant.is_active
            )

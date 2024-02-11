import uuid
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField, BooleanField, DateTimeField, ForeignKey
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from news_buzz.users.managers import UserManager
from django_extensions.db.models import TimeStampedModel


class User(AbstractUser):
    """
    Default custom user model for News Buzz.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class Participant(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant_id = CharField(_("Id of Participant"), max_length=255, unique=True)
    is_active = BooleanField(_("is participant active"), default=True)
    first_name = models.CharField(_("First Name of Participant"), max_length=255, null=True, blank=True, default=None)
    login_website_type = models.CharField(
        _("Website accesed High / Low PC1"), max_length=255, null=True, blank=True, default=None
    )

    def __str__(self) -> str:
        return self.participant_id


class Session(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant = ForeignKey(Participant, related_name="sessions", on_delete=models.CASCADE)
    is_active = BooleanField(_("is session active"), default=True)
    end_time = DateTimeField(_("time session ended"), null=True, blank=True, default=None)

    def __str__(self) -> str:
        return str(self.id)

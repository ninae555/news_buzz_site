
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from .models import Participant
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


class ParticipantDetailView(DetailView):
    model = Participant
    slug_field = "id_of_participant"
    slug_url_kwarg = "id_of_participant"


participant_detail_view = ParticipantDetailView.as_view()


class ParticipantUpdateView(UpdateView):
    model = Participant
    fields = []  # If you have additional fields for participants, list them here
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return reverse("participants:detail", kwargs={"id_of_participant": self.request.user.id_of_participant})

    def get_object(self):
        return self.request.user  # Assumes you've set the Participant as the user model in settings


participant_update_view = ParticipantUpdateView.as_view()

class ParticipantIDBackend(ModelBackend):
    def authenticate(self, request, id_of_participant=None, **kwargs):
        try:
            participant = Participant.objects.get(id_of_participant=id_of_participant)
            return participant
        except Participant.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Participant.objects.get(pk=user_id)
        except Participant.DoesNotExist:
            return None


def participant_login(request):
    if request.method == "POST":
        id_of_participant = request.POST.get('id_of_participant')
        participant = authenticate(request, id_of_participant=id_of_participant)
        if participant:
            request.session['participant_id'] = id_of_participant
            login(request, participant)
            return redirect('home.html')  # Replace with your desired redirect view
        else:
            # Provide feedback to the user if the ID is incorrect
            return render(request, 'login.html', {'error': 'Invalid Participant ID'})

    return render(request, 'login.html')

class ParticipantRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


participant_redirect_view = ParticipantRedirectView.as_view()
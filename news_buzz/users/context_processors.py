from django.conf import settings
from news_buzz.articles.models import SurveyReminder


def allauth_settings(request):
    """Expose some settings from django-allauth in templates."""
    return {
        "ACCOUNT_ALLOW_REGISTRATION": settings.ACCOUNT_ALLOW_REGISTRATION,
    }


def survey_reminder(request):
    """Expose some settings from django-allauth in templates."""
    return {
        "survey_reminder": SurveyReminder.objects.first(),
    }

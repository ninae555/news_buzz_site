from django.urls import path

from news_buzz.users.views import (
    participant_detail_view,
    participant_redirect_view,
    participant_update_view,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=participant_redirect_view, name="redirect"),
    path("~update/", view=participant_update_view, name="update"),
    path("<int:pk>/", view=participant_detail_view, name="detail"),
]

from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from climate_buzz.users.api.views import UserViewSet
from climate_buzz.articles.api.views import ArticleViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("articles", ArticleViewSet)


app_name = "api"
urlpatterns = router.urls

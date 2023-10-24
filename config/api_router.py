from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from news_buzz.users.api.views import UserViewSet, ParticipantViewSet
from news_buzz.articles.api.views import ArticleViewSet,ReactionViewSet, CommentViewSet, ReadEntireArticleClickViewSet


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("articles", ArticleViewSet)
router.register(r'reactions', ReactionViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'participants', ParticipantViewSet)
router.register(r'read-entire-article-clicks', ReadEntireArticleClickViewSet)

app_name = "api"
urlpatterns = router.urls

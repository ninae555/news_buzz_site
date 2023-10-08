from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from articles.models import Article
from .serializers import ArticleSerializer


class ArticleViewSet(ListModelMixin, GenericViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all().values(
        "id",
        "url",
        "description",
        "title",
        "image_url",
        "author",
        "publisher__domain",
        "published_at",
    )

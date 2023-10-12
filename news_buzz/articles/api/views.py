from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from articles.models import Article
from .serializers import ArticleSerializer
from rest_framework import viewsets
from articles.models import Reaction, Comment
from .serializers import LikeSerializer, CommentSerializer


class ArticleViewSet(ListModelMixin, GenericViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = ArticleSerializer
    queryset = Article.objects.filter(publisher__is_excluded=False).values(
        "id",
        "url",
        "description",
        "title",
        "image_url",
        "author",
        "publisher__domain",
        "published_at",
    )

class LikeViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = LikeSerializer
    queryset = Reaction.objects.all()

class CommentViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin,GenericViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
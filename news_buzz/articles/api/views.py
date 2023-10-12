from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from articles.models import Article
from .serializers import ArticleSerializer
from rest_framework import viewsets
from articles.models import Like, Comment
from .serializers import LikeSerializer, CommentSerializer


class ArticleViewSet(ListModelMixin, GenericViewSet):
    authentication_classes = []
    permission_classes = []
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

class LikeViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

class CommentViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
from typing import Any
from django.db.models.query import QuerySet
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from news_buzz.articles.models import Article
from .serializers import ArticleSerializer
from news_buzz.articles.models import Reaction, Comment, ReadEntireArticleClick, ArticleSent
from .serializers import (
    ReactionSerializer,
    CommentSerializer,
    ReadEntireArticleClickSerializer,
)
from django.db.models import OuterRef, Subquery
from .permissions import IsValidParticipantSession


class ArticleViewSet(ListModelMixin, GenericViewSet):
    authentication_classes = []
    permission_classes = [IsValidParticipantSession]
    serializer_class = ArticleSerializer
    queryset = (
        Article.objects.filter(publisher__is_excluded=False, hide=False)
        .values(
            "id",
            "url",
            "description",
            "title",
            "image_url",
            "author",
            "publisher__domain",
            "published_at",
        )
        .order_by("-published_at")
    )

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .annotate(
                reaction=Subquery(
                    Reaction.objects.filter(
                        participant_id=self.request.participant_session.participant.id,
                        article_id=OuterRef("id"),
                    ).values("type")[:1]
                )
            )
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            ArticleSent.objects.bulk_create([ArticleSent(article_id=article["id"], session_id=request.participant_session.id) for article in page])

            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ReactionViewSet(CreateModelMixin, GenericViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = ReactionSerializer
    queryset = Reaction.objects.all()

    @action(detail=False, methods=["delete"])
    def delete_reaction(self, request):
        serializer = ReactionSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        Reaction.objects.filter(participant_id=request.data["participant"], article_id=request.data["article"]).delete()
        return Response(status=status.HTTP_201_CREATED, data={"message": "Reaction deleted successfully."})

class CommentViewSet(
    ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet
):
    authentication_classes = []
    permission_classes = []
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class ReadEntireArticleClickViewSet(CreateModelMixin, GenericViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = ReadEntireArticleClick.objects.all()
    serializer_class = ReadEntireArticleClickSerializer

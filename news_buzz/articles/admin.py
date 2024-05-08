from django.contrib import admin
from import_export.admin import ImportExportMixin
from news_buzz.articles.models import (
    Article,
    Publisher,
    ArticleSent,
    Reaction,
    ReadEntireArticleClick,
    Category,
    Comment,
    SurveyReminder,
)
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class ReactionResource(resources.ModelResource):

    class Meta:
        model = Reaction
        fields = (
            "id",
            "created",
            "type",
            "participant",
            "participant__participant_id",
            "article",
            "article__title",
            "categories",
        )


class ReadEntireArticleClickResource(resources.ModelResource):
    class Meta:
        model = ReadEntireArticleClick
        fields = (
            "id",
            "participant",
            "session",
            "article__title",
            "categories",
        )


@admin.register(Publisher)
class PublisherAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "domain", "name", "pc1", "created", "modified"]
    search_fields = ["domain", "id", "name"]


@admin.register(Category)
class CategoryAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "name", "created", "modified"]
    search_fields = ["name", "id"]


@admin.register(Comment)
class CommentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "article", "content", "session", "created", "modified"]
    search_fields = [
        "content",
        "id",
        "article",
        "session",
    ]
    raw_id_fields = ["article", "session"]


@admin.register(Article)
class ArticleAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "published_at", "publisher", "title", "url", "created", "modified"]
    search_fields = ["title", "id"]


@admin.register(ReadEntireArticleClick)
class ReadEntireArticleClickAdmin(ImportExportModelAdmin):
    resource_class = ReadEntireArticleClickResource
    list_display = ["id", "participant", "session", "article"]


@admin.register(ArticleSent)
class ArticleSentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "session", "article"]


@admin.register(Reaction)
class ReactionAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "participant", "article", "type"]
    resource_class = ReactionResource


@admin.register(SurveyReminder)
class SurveyReminderAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "created", "modified"]
    search_fields = [
        "id",
        "title",
    ]

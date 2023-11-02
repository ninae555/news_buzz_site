from django.contrib import admin
from import_export.admin import ImportExportMixin 
from news_buzz.articles.models import Article, Publisher, ArticleSent, ArticleTimeSpent, Reaction, ReadEntireArticleClick, Category

@admin.register(Publisher)
class PublisherAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "domain", "pc1", "created", "modified"]


@admin.register(Category)
class CategoryAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "name", "created", "modified"]
    search_fields = ["name", "id"]

@admin.register(Article)
class ArticleAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "published_at", "publisher", "title", "url", "created", "modified"]
    search_fields = ["title", "id"]

@admin.register(ReadEntireArticleClick)
class ReadEntireArticleClickAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "participant", "session", "article"]

@admin.register(ArticleSent)
class ArticleSentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "session", "article"]

@admin.register(Reaction)
class ReactionAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["id", "participant", "article", "type"]

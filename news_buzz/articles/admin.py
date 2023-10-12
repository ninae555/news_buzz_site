from django.contrib import admin
from articles.models import Article, Publisher, Participant

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ["id", "domain", "pc1", "created", "modified"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "publisher", "title", "url", "created", "modified"]


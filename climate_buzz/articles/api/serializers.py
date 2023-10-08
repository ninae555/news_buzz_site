from rest_framework import serializers
from articles.models import Article



class ArticleSerializer(serializers.ModelSerializer):
    publisher = serializers.CharField(source="publisher__domain")
    class Meta:
        model = Article
        fields = ["id", "url", "description", "title", "image_url", "author", "publisher", "published_at"]

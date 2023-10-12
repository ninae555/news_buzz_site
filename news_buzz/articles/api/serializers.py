from rest_framework import serializers
from articles.models import Article
from articles.models import Reaction, Comment


class ArticleSerializer(serializers.ModelSerializer):
    publisher = serializers.CharField(source="publisher__domain")
    class Meta:
        model = Article
        fields = ["id", "url", "description", "title", "image_url", "author", "publisher", "published_at"]

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
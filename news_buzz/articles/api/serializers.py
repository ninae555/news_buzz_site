from rest_framework import serializers
from news_buzz.articles.models import Article
from news_buzz.articles.models import Reaction, Comment


class ArticleSerializer(serializers.ModelSerializer):
    publisher = serializers.CharField(source="publisher__domain")
    class Meta:
        model = Article
        fields = ["id", "url", "description", "title", "image_url", "author", "publisher", "published_at"]

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ["id", "type", "participant", "article"]

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
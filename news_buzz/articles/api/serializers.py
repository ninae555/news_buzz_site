from typing import Any
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from news_buzz.articles.models import Article
from news_buzz.articles.models import Reaction, Comment, ReadEntireArticleClick


class ArticleSerializer(serializers.ModelSerializer):
    publisher = serializers.CharField(source="publisher__domain")
    reaction = serializers.CharField()

    class Meta:
        model = Article
        fields = ["id", "url", "description", "title", "image_url", "author", "publisher", "published_at", "reaction"]

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ["id", "type", "participant", "article", "session"]

    def get_unique_together_validators(self) -> list[UniqueTogetherValidator]:
        return []

    def validate(self, attrs: Any) -> Any:
        if not attrs["session"].is_active:
            raise serializers.ValidationError("Invalid session")
        if not attrs["participant"].is_active:
            raise serializers.ValidationError("Invalid credentials")
        if attrs["session"].participant_id != attrs["participant"].id:
            raise serializers.ValidationError("Invalid details")
        return super().validate(attrs)
    
    def create(self, validated_data):
        participant = validated_data.get('participant')
        article = validated_data.get('article')
        session = validated_data.get('session')
        reaction_type = validated_data.get('type')        
        reaction, _ = Reaction.objects.update_or_create(
            participant=participant,
            article=article,
            defaults={'type': reaction_type, "session":session}
        )
        return reaction
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class ReadEntireArticleClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadEntireArticleClick
        fields = ["id", "session", "participant", "article"]

    def validate(self, attrs: Any) -> Any:
        if not attrs["session"].is_active:
            raise serializers.ValidationError("Invalid session")
        if not attrs["participant"].is_active:
            raise serializers.ValidationError("Invalid credentials")
        if attrs["session"].participant_id != attrs["participant"].id:
            raise serializers.ValidationError("Invalid details")
        return super().validate(attrs)
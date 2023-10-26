from django.db import models
from django_extensions.db.models import TimeStampedModel
from news_buzz.users.models import Session, Participant


class Publisher(TimeStampedModel):
    domain = models.CharField(max_length=255, unique=True)
    pc1 = models.FloatField()
    is_excluded = models.BooleanField(default=False)

    def __str__(self):
        return self.domain


class Article(TimeStampedModel):
    title = models.CharField(max_length=1000)
    content = models.TextField()
    url = models.URLField(max_length=1000, unique=True)
    description = models.TextField(null=True, blank=True)
    publisher = models.ForeignKey(
        Publisher, related_name="articles", on_delete=models.CASCADE
    )
    image_url = models.URLField(max_length=1000, null=True, blank=True)
    published_at = models.DateTimeField()
    author = models.CharField(max_length=255, null=True, blank=True)
    hide = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Reaction(TimeStampedModel):
    LIKE = "L"
    LOVE = "LV"
    CARE = "C"
    WOW = "W"
    HAHA = "H"
    SAD = "S"
    ANGRY = "A"

    REACTION_TYPES = [
        (LIKE, "Like"),
        (LOVE, "Love"),
        (CARE, "Care"),
        (WOW, "WOW"),
        (HAHA, "Haha"),
        (SAD, "Sad"),
        (ANGRY, "Angry"),
    ]
    type = models.CharField(max_length=3, choices=REACTION_TYPES)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("participant", "article")


class Comment(TimeStampedModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField()


class ReadEntireArticleClick(TimeStampedModel):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class ShareClick(TimeStampedModel):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

class ArticleTimeSpent(TimeStampedModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        unique_together = ("session", "article")


class ArticleSent(TimeStampedModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

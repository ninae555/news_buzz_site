from django.contrib.auth import get_user_model
from django.utils import timezone
from config import celery_app
from news_buzz.articles.models import Article, Publisher
from newsapi import NewsApiClient
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import tldextract

User = get_user_model()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()

def chunker(seq, size):
    """Splits the list into chunks of the given size."""
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

@celery_app.task()
def fetch_articles():
    newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)
    eligible_publishers = dict(Publisher.objects.filter(pc1__lte=0.5, is_excluded=False).values_list("domain", "id"))
    
    for chunk in chunker(list(eligible_publishers.keys()), 500):
        params={
            "q": "climate change OR global warming OR climate crisis OR sustainability OR renewable energy",
            "domains": ",".join(chunk),
            "from_param": (timezone.now().date()- timedelta(days=2)).isoformat(),
            "to": timezone.now().date().isoformat(),
            "language":'en',
            "sort_by": "popularity",
        }
        response = newsapi.get_everything(**params)
        print(response)
        articles= response["articles"]
        # Debugging
        print(f"Type of articles: {type(articles)}")
        if articles:
            print(f"First article: {articles[0]}")
        else:
            print('No articles found')
            return
        articles_to_create = []
        # Process articles
        for article in articles:
            if not Article.objects.filter(url=article['url']).exists():
                url_components = tldextract.extract(article['url']) 
                article_domain = url_components.domain + "." + url_components.suffix
                publisher_id=eligible_publishers.get(article_domain.lower())
                if publisher_id:
                    articles_to_create.append(Article(
                        title=article['title'],
                        content=article['content'],
                        author=article['author'],
                        url=article['url'],
                        image_url=article['urlToImage'],
                        published_at=article['publishedAt'],
                        description=article['description'],
                        publisher_id=publisher_id

                    ))
                else:
                    print(f'Error processing article could now found publisher: {article}')

        articles_created = Article.objects.bulk_create(articles_to_create)
        print(f'articles created: {articles_created}')







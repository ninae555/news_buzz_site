from django.core.management.base import BaseCommand
from news_buzz.articles.models import Article, Publisher
from newsapi import NewsApiClient
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import tldextract

class Command(BaseCommand):
    help = 'Fetch and process articles'

    def handle(self, *args, **kwargs):
        newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)
        # eligible_publishers = dict(Publisher.objects.filter(pc1__lte=0.5).values_list("domain", "id"))
        params={
            "q": "climate change OR global warming OR climate crisis OR sustainability OR renewable energy",
            # "domains": ",".join(list(eligible_publishers.keys())[:500]),
            "from_param": (timezone.now().date()- timedelta(days=3)).isoformat(),
            "to": timezone.now().date().isoformat(),
            "language":'en',
            "sort_by": "popularity",
            "page": 0
        }
        while True:
            params["page"] +=1
            response = newsapi.get_everything(**params)
            articles= response["articles"]
            if articles:
                print(f"First article: {articles[0]}")
            else:
                print(('No articles found'))
                break
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
                # else:
                #     print((f'Error processing article could now found publisher: {article}'))

            articles_created = Article.objects.bulk_create(articles_to_create)
            print((f'articles created: {articles_created}'))






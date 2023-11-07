from django.utils import timezone
from config import celery_app
from news_buzz.articles.models import Article, Publisher, Category
from newsapi import NewsApiClient
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import tldextract
import spacy
from spacy.matcher import PhraseMatcher

BROAD_KEYWORDS = [
        "climate", "carbon", "greenhouse", "global warming", "sustainability", 
        "renewable", "deforest", "emission", "fossil fuel", "solar", 
        "wind energy", "recycle", "conserve", "environment", "pollute", 
        "eco-friendly", "clean energy", "EV", "electric vehicle", "zero-emission",
        "carbon-neutral", "biofuel", "geothermal", "hydropower", "tidal energy", 
        "ozone", "melt glacier", "sea-level rise", "greenwash"
    ]
NLP_MODEL = spacy.load("en_core_web_sm")
MATCHER = PhraseMatcher(NLP_MODEL.vocab, attr='LEMMA')
MATCHER.add("ClimateChangeKeywords", [NLP_MODEL(keyword) for keyword in BROAD_KEYWORDS])


def has_broad_keyword(content):
    doc = NLP_MODEL(content.lower())
    matches = MATCHER(doc)
    return len(matches) > 0


def chunker(seq, size):
    """Splits the list into chunks of the given size."""
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

@celery_app.task()
def fetch_articles():
    climate_category, _ = Category.objects.get_or_create(name="Climate")
    newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)
    eligible_publishers = dict(Publisher.objects.filter(is_excluded=False).values_list("domain", "id"))    
    params={
        "q": "climate change OR global warming OR climate crisis OR sustainability OR renewable energy",
        "from_param": (timezone.now().date()- timedelta(days=2)).isoformat(),
        "to": timezone.now().date().isoformat(),
        "language":'en',
        "sort_by": "popularity",
        "page": 0
    }
    while True:
        params["page"] +=1
        response = newsapi.get_everything(**params)
        print(response)
        articles= response["articles"]
        # Debugging
        print(f"Type of articles: {type(articles)}")
        if articles:
            print(f"First article: {articles[0]}")
        else:
            print('No articles found')
            break
        articles_to_create = []
        articles_categories_to_create = []
        
        # Process articles
        for article in articles:
            if not Article.objects.filter(url=article['url']).exists():
                url_components = tldextract.extract(article['url']) 
                article_domain = url_components.domain + "." + url_components.suffix
                publisher_id=eligible_publishers.get(article_domain.lower())
                if publisher_id:
                    article_obj=Article(
                        title=article['title'],
                        content=article['content'],
                        author=article['author'],
                        url=article['url'],
                        image_url=article['urlToImage'],
                        published_at=article['publishedAt'],
                        description=article['description'],
                        publisher_id=publisher_id
                    )
                    articles_to_create.append(article_obj)
                    if has_broad_keyword((article["content"] if article["content"] else "")  + " \n "+ (article["description"] if article["description"] else "")):
                        articles_categories_to_create.append(Article.categories.through(category=climate_category, article=article_obj))
                else:
                    print(f'Error processing article could not found publisher: {article}')

        articles_created = Article.objects.bulk_create(articles_to_create)
        Article.categories.through.objects.bulk_create(articles_categories_to_create)
        print(f'articles created: {articles_created}')







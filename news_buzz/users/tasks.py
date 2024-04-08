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
import re
import requests
from spacy.lang.en import English
import random


# Load English tokenizer
nlp = English()


def clean_text(text):
    """Clean and normalize text."""
    # Remove HTML tags and special characters
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text, re.I | re.A)
    # Remove extra spaces and tabs
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text):
    """Tokenize the text."""
    doc = nlp(text)
    return [token.text for token in doc]


def remove_stop_words(tokens):
    """Remove stop words from the list of tokens."""
    return [token for token in tokens if token not in nlp.Defaults.stop_words]


def lemmatize(tokens):
    """Lemmatize the tokens."""
    doc = nlp(" ".join(tokens))
    return [token.lemma_ for token in doc]

BROAD_KEYWORDS = [
    "biodiversity",
    "biofuel",
    "carbon emissions",
    "carbon neutral",
    "clean energy",
    "climate adaptation",
    "climate change",
    "climate crisis",
    "climate emergency",
    "climate mitigation",
    "climate policy",
    "climate resilience",
    "climate science",
    "conservation",
    "conserve",
    "deforest",
    "drought",
    "eco-friendly",
    "electric vehicle",
    "emission",
    "energy transition",
    "environment",
    "environmental activism",
    "environmental impact",
    "environmental policy",
    "environmental protection",
    "extreme weather",
    "flooding",
    "fossil fuel",
    "geothermal",
    "global warming",
    "greenhouse gases",
    "greenwash",
    "hydropower",
    "melt glacier",
    "natural resources",
    "ozone",
    "pollute",
    "recycle",
    "renewable",
    "renewable energy",
    "sea level rise",
    "solar energy",
    "sustainable energy",
    "tidal energy",
    "wildfires",
    "wind energy",
    "wind power",
    "zero emissions",
]


NLP_MODEL = spacy.load("en_core_web_sm")
MATCHER = PhraseMatcher(NLP_MODEL.vocab, attr="LEMMA")
MATCHER.add("ClimateChangeKeywords", [NLP_MODEL(keyword) for keyword in BROAD_KEYWORDS])


def has_broad_keyword(preprocessed_content):
    doc = NLP_MODEL(preprocessed_content.lower())
    matches = MATCHER(doc)
    return len(matches) > 0


def chunker(seq, size):
    """Splits the list into chunks of the given size."""
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


@celery_app.task()
def fetch_articles():
    climate_category, _ = Category.objects.get_or_create(name="Climate")
    newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)
    eligible_publishers = dict(Publisher.objects.filter(is_excluded=False).values_list("domain", "id"))
    params = {
        "from_param": (timezone.now().date() - timedelta(days=10)).isoformat(),
        "to": timezone.now().date().isoformat(),
        "language": "en",
        # "pageSize": 100,
        "sort_by": "popularity",
        "page": 0,
    }

    # all_lemmatized_texts = []  # To store lemmatized texts from all articles
    for q in [" OR ".join(BROAD_KEYWORDS[:len(BROAD_KEYWORDS)//2]), " OR ".join(BROAD_KEYWORDS[len(BROAD_KEYWORDS) // 2:])]:
        params["q"] = q 
        params["page"] = 0
        print(q) 
        while True:
            params["page"] += 1
            response = newsapi.get_everything(**params)
            articles = response["articles"]
            # Debugging
            print(f"climate request response page: {params['page']}")
            print(response["totalResults"])
            if articles:
                print(f"articles found: {len(articles)}")
            else:
                print("No articles found")
                break
            articles_to_create = []
            articles_categories_to_create = []

            # Process articles
            for article in articles:
                if not Article.objects.filter(url=article["url"]).exists() and article["content"]:
                    if article["author"] and (len(article["author"])) > 255:
                        print("author length more")
                        print(article["author"])
                        continue
                    url_components = tldextract.extract(article["url"])
                    article_domain = url_components.domain + "." + url_components.suffix
                    publisher_id = eligible_publishers.get(article_domain.lower())

                    # Preprocess the article content
                    cleaned_content = clean_text(
                        (article["title"] if article["title"] else "")
                        + " "
                        + (article["description"] if article["description"] else "")
                        + " "
                        + (article["content"] if article["content"] else "")
                    )
                    tokens = tokenize(cleaned_content)
                    tokens = remove_stop_words(tokens)
                    # lemmatized_tokens = lemmatize(tokens)
                    preprocessed_content = " ".join(tokens)

                    if publisher_id:
                        article_obj = Article(
                            title=article["title"],
                            content=article["content"],
                            author=article["author"],
                            url=article["url"],
                            image_url=article["urlToImage"],
                            published_at=article["publishedAt"],
                            description=article["description"],
                            publisher_id=publisher_id,
                        )
                        articles_to_create.append(article_obj)
                        if has_broad_keyword(preprocessed_content):
                            articles_categories_to_create.append(
                                Article.categories.through(category=climate_category, article=article_obj)
                            )
                    else:
                        print(f'Error processing article could not found publisher: {article["url"]}')

            articles_created = Article.objects.bulk_create(articles_to_create)
            Article.categories.through.objects.bulk_create(articles_categories_to_create)
            print(f"articles created: {articles_created}")

    domains = list(
        Publisher.objects.filter(articles__isnull=False, pc1__gte=0, pc1__lte=0.25)
        .values_list("domain", flat=True)
        .distinct()
    )
    # Initialize an empty set for the paired domains
    paired_domains = []

    # Iterate over the list in steps of 2
    for i in range(0, len(domains), 2):
        # Check if the second element of the pair exists
        if i + 1 < len(domains):
            # Join the two domains with a comma and add to the set
            pair = ",".join([domains[i], domains[i + 1]])
            paired_domains.append(pair)
        else:
            # If it's the last element without a pair, just append it alone
            paired_domains.append(domains[i])

    selected_pairs = []
    try:
        selected_pairs = random.sample(paired_domains, 7)
    except ValueError:
        # In case there are fewer than 7 pairs, select all available pairs
        selected_pairs = list(paired_domains)
    for domain in selected_pairs:
        for q in [" OR ".join(BROAD_KEYWORDS[:len(BROAD_KEYWORDS)//2]), " OR ".join(BROAD_KEYWORDS[len(BROAD_KEYWORDS) // 2:])]:
            params = {
                "q": q, 
                "language": "en",
                # "country":'us',
                # "sort_by": "popularity",
                # "page": 2,
                "from_param": (timezone.now().date() - timedelta(days=10)).isoformat(),
                "to": timezone.now().date().isoformat(),
                "domains": domain,
                "pageSize": 100,
                "apiKey": settings.NEWS_API_KEY,
            }
            response = requests.get(url="https://newsapi.org/v2/everything", params=params)
            response = response.json()
            print(response["totalResults"])
            articles = response["articles"]
            if articles:
                print(f"articles found: {len(articles)}")
                articles_to_create = []
                articles_categories_to_create = []

                for article in articles:
                    if not Article.objects.filter(url=article["url"]).exists() and article["content"]:
                        if article["author"] and (len(article["author"])) > 255:
                            print("author length more")
                            print(article["author"])
                            continue
                        url_components = tldextract.extract(article["url"])
                        article_domain = url_components.domain + "." + url_components.suffix
                        publisher_id = eligible_publishers.get(article_domain.lower())

                        # Preprocess the article content
                        cleaned_content = clean_text(
                            (article["title"] if article["title"] else "")
                            + " "
                            + (article["description"] if article["description"] else "")
                            + " "
                            + (article["content"] if article["content"] else "")
                        )
                        tokens = tokenize(cleaned_content)
                        tokens = remove_stop_words(tokens)
                        # lemmatized_tokens = lemmatize(tokens)
                        preprocessed_content = " ".join(tokens)

                        if publisher_id:
                            article_obj = Article(
                                title=article["title"],
                                content=article["content"],
                                author=article["author"],
                                url=article["url"],
                                image_url=article["urlToImage"],
                                published_at=article["publishedAt"],
                                description=article["description"],
                                publisher_id=publisher_id,
                            )
                            articles_to_create.append(article_obj)
                            # Use preprocessed content for keyword matching
                            if has_broad_keyword(preprocessed_content):
                                articles_categories_to_create.append(
                                    Article.categories.through(category=climate_category, article=article_obj)
                                )
                        else:
                            print(f'Error processing article could not found publisher: {article["url"]}')

                articles_created = Article.objects.bulk_create(articles_to_create)
                Article.categories.through.objects.bulk_create(articles_categories_to_create)
                print(f"articles created: {len(articles_created)}")

    for category in ["Business", "Entertainment", "General", "Health", "Science", "Sports", "Technology"]:
        category, _ = Category.objects.get_or_create(name=category)
        params = {
            # "q": "",
            "language": "en",
            # "country":'us',
            # "sort_by": "popularity",
            "category": category.name.lower(),
            # "page": 2,
            "pageSize": 100,
            "apiKey": settings.NEWS_API_KEY,
        }
        response = requests.get(url="https://newsapi.org/v2/top-headlines", params=params)
        response = response.json()
        print(f"{category.name}")
        print(response["totalResults"])
        articles = response["articles"]
        if articles:
            print(f"articles found: {len(articles)}")
            articles_to_create = []
            articles_categories_to_create = []

            for article in articles:
                if not Article.objects.filter(url=article["url"]).exists() and article["content"]:
                    if article["author"] and (len(article["author"])) > 255:
                        print("author length more")
                        print(article["author"])
                        continue
                    url_components = tldextract.extract(article["url"])
                    article_domain = url_components.domain + "." + url_components.suffix
                    publisher_id = eligible_publishers.get(article_domain.lower())

                    # Preprocess the article content
                    cleaned_content = clean_text(
                        (article["title"] if article["title"] else "")
                        + " "
                        + (article["description"] if article["description"] else "")
                        + " "
                        + (article["content"] if article["content"] else "")
                    )
                    tokens = tokenize(cleaned_content)
                    tokens = remove_stop_words(tokens)
                    # lemmatized_tokens = lemmatize(tokens)
                    preprocessed_content = " ".join(tokens)  # Join the lemmatized tokens

                    if publisher_id:
                        article_obj = Article(
                            title=article["title"],
                            content=article["content"],
                            author=article["author"],
                            url=article["url"],
                            image_url=article["urlToImage"],
                            published_at=article["publishedAt"],
                            description=article["description"],
                            publisher_id=publisher_id,
                        )
                        articles_to_create.append(article_obj)
                        articles_categories_to_create.append(
                            Article.categories.through(category=category, article=article_obj)
                        )
                        # Use preprocessed content for keyword matching
                        if has_broad_keyword(preprocessed_content):
                            articles_categories_to_create.append(
                                Article.categories.through(category=climate_category, article=article_obj)
                            )
                    else:
                        print(f'Error processing article could not found publisher: {article["url"]}')

            articles_created = Article.objects.bulk_create(articles_to_create)
            Article.categories.through.objects.bulk_create(articles_categories_to_create)
            print(f"articles created: {len(articles_created)}")


def check_climate_categoryin_articles():
    climate_category, _ = Category.objects.get_or_create(name="Climate")
    articles = Article.objects.values().exclude(categories=climate_category)
    print(len(articles))
    for article in articles:
        cleaned_content = clean_text(
            (article["title"] if article["title"] else "")
            + " "
            + (article["description"] if article["description"] else "")
            + " "
            + (article["content"] if article["content"] else "")
        )
        tokens = tokenize(cleaned_content)
        tokens = remove_stop_words(tokens)
        preprocessed_content = " ".join(tokens)  # Join the lemmatized tokens
        if has_broad_keyword(preprocessed_content):
            print(article["id"])
            print(article["created"])
            Article.categories.through.objects.create(category=climate_category, article_id=article["id"])

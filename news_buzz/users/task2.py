
from news_buzz.users.tasks import *

def fetch_articles():
    print("7")
    climate_category, _ = Category.objects.get_or_create(name="Climate")
    eligible_publishers = dict(Publisher.objects.filter(is_excluded=False).values_list("domain", "id"))
    domains = list(
        Publisher.objects.filter(articles__isnull=False, is_excluded=False)
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
        selected_pairs = random.sample(paired_domains, 20)
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

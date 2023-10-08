from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer
from django.shortcuts import get_object_or_404
from .data_processing import NewsDataProcessor
from myapp.management.commands.fetch_articles import Command as FetchArticlesCommand
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Like, Article  # Assuming the Like model and Article model are in the same models.py file
from django.contrib.auth.decorators import login_required




# Create instances of the classes
data_processor = NewsDataProcessor()
article_fetcher = FetchArticlesCommand()  # Replace with the correct class name if different

def home(request):
    articles = Article.objects.all().order_by('-id')
    return render(request, 'myapp/list_articles.html', {'articles': articles})


def list_articles(request):
    articles = Article.objects.all().order_by('-id')
    return render(request, 'myapp/list_articles.html', {'articles': articles})

def view_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'myapp/article_detail.html', {'article': article})

def list_domains(request):
    df_articles = data_processor.get_articles()
    df_articles['domain'] = df_articles['url'].apply(data_processor.extract_domain)
    found_domains, not_found_domains, df_articles = data_processor.check_domains(df_articles, data_processor.high_quality_domains, data_processor.generate_domain_representations)
    context = {
        'found_domains': found_domains,
        'not_found_domains': not_found_domains,
    }
    return render(request, 'myapp/domains.html', context)


@api_view(['POST'])

def add_article(request):
    if request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            # Process the title using your method
           # processed_title = data_processor.process_article_title(serializer.validated_data['title'])
            processed_title = NewsDataProcessor.get_articles(serializer.validated_data['title'])

            # If you want to modify the title before saving:
            serializer.validated_data['title'] = processed_title

            # Save processed data or additional actions
            article = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@login_required
def profile(request):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if p_form.is_valid():
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')

    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)
def login_view(request):
    error_message = None
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        print("Login form data:", request.POST)  # Debug line
        if user is not None:
            print("User is authenticated")  # Debug line
            login(request, user)
            return redirect('home')
        else:
            error_message = "Invalid username or password"
            print("Authentication failed")  # Debug line

    return render(request, 'registration/login.html', {'error': error_message})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print("Signup form data:", request.POST)  # Debug line
        if form.is_valid():
            print("Form is valid")  # Debug line
            user = form.save()
            login(request, user)
            return redirect('home')
    else:  # This will handle the GET request
        form = UserCreationForm()

    # Render the form, either with or without errors
    return render(request, 'registration/signup.html', {'form': form})

@csrf_exempt
@login_required
def like_article(request):
    if request.method == "POST":
        data = json.loads(request.body)
        article_id = data.get('article_id')

        # Assuming you have a Like model as discussed previously
        like = Like(user=request.user, article_id=article_id)
        like.save()

        return JsonResponse({"message": "Article liked!"}, status=201)

    return JsonResponse({"error": "Invalid request method"}, status=405)
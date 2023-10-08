from django.urls import path, include
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from django.contrib import admin


from . import views
app_name = 'myapp'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='articles/')),
    path('articles/', views.list_articles, name='list_articles'),
    path('api/add_article/', views.add_article, name='add_article'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('domains/', views.list_domains, name='view_domains'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('article/<int:article_id>/', views.view_article, name='view_article'),

]
# from django.urls import path
# from django.http import HttpResponse


# urlpatterns = [
#     path('test/', lambda request: HttpResponse('Test')),
#     path('admin/', admin.site.urls),
# ]

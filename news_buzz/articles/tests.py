from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Article

class LikeArticleTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@email.com', 'testpassword')
        self.article = Article.objects.create(...) # fill in the required fields
    
    def test_like_article(self):
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.post('/api/like/', {'article_id': self.article.id}, content_type='application/json')
        
        self.assertEqual(response.status_code, 201)

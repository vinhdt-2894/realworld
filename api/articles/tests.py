from rest_framework.test import APITestCase
from rest_framework import status
from api.articles.models import Article, Comment
from api.users.models import CustomUser

API_PREFIX = "/api/v1"


class ArticleDetailAndCommentAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="author1", email="author1@example.com", password="testpass"
        )
        self.other_user = CustomUser.objects.create_user(
            username="author2", email="author2@example.com", password="testpass2"
        )
        self.article = Article.objects.create(
            slug="article-1",
            title="Article 1",
            description="Description 1",
            body="Body 1",
            author=self.user,
        )
        self.detail_url = f"{API_PREFIX}/articles/{self.article.slug}/"
        self.comments_url = f"{API_PREFIX}/articles/{self.article.slug}/comments/"
        self.favorite_url = f"{API_PREFIX}/articles/{self.article.slug}/favorite/"

    def authenticate(self, user):
        login_url = f"{API_PREFIX}/users/login/"
        login_data = {
            "user": {
                "email": user.email,
                "password": "testpass" if user == self.user else "testpass2",
            }
        }
        response = self.client.post(login_url, login_data, format="json")
        token = response.data["user"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_article_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["article"]["title"], "Article 1")
        self.assertEqual(response.data["article"]["author"], "author1")

    def test_favorite_article_requires_auth(self):
        response = self.client.post(self.favorite_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_favorite_and_unfavorite_article(self):
        self.authenticate(self.user)
        # Favorite
        response = self.client.post(self.favorite_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            self.user, Article.objects.get(pk=self.article.pk).favorited_by.all()
        )
        # Unfavorite
        response = self.client.delete(self.favorite_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(
            self.user, Article.objects.get(pk=self.article.pk).favorited_by.all()
        )

    def test_create_comment_requires_auth(self):
        data = {"body": "A comment"}
        response = self.client.post(self.comments_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_and_delete_comment(self):
        self.authenticate(self.user)
        # Create comment
        data = {"body": "A comment"}
        response = self.client.post(self.comments_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment_id = response.data["comment"]["id"]
        # Only author can delete
        delete_url = f"{API_PREFIX}/articles/{self.article.slug}/comments/{comment_id}/"
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Other user cannot delete
        comment = Comment.objects.create(
            article=self.article, author=self.user, body="Another comment"
        )
        self.authenticate(self.other_user)
        delete_url = f"{API_PREFIX}/articles/{self.article.slug}/comments/{comment.id}/"
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

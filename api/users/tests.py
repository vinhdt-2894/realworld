from rest_framework.test import APITestCase
from rest_framework import status
from api.users.models import CustomUser

API_PREFIX = "/api/v1"


class UserLoginAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )
        self.login_url = f"{API_PREFIX}/users/login/"

    def test_login_success(self):
        data = {
            "user": {"email": "testuser@example.com", "password": "testpassword123"}
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data["user"])
        self.assertEqual(response.data["user"]["email"], "testuser@example.com")

    def test_login_wrong_password(self):
        data = {"user": {"email": "testuser@example.com", "password": "wrongpassword"}}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "non_field_errors", response.data or response.data.get("user", {})
        )

    def test_login_nonexistent_email(self):
        data = {
            "user": {"email": "notfound@example.com", "password": "testpassword123"}
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "non_field_errors", response.data or response.data.get("user", {})
        )


class UserRegisterAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = f"{API_PREFIX}/users/"

    def test_register_success(self):
        data = {
            "user": {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword123",
            }
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data["user"])
        self.assertEqual(response.data["user"]["email"], "newuser@example.com")
        self.assertTrue(CustomUser.objects.filter(email="newuser@example.com").exists())

    def test_register_missing_field(self):
        data = {
            "user": {
                "username": "",
                "email": "invalid@example.com",
                "password": "pass",
            }
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "username",
            response.data["user"] if "user" in response.data else response.data,
        )

    def test_register_duplicate_email(self):
        CustomUser.objects.create_user(
            username="dupuser", email="dup@example.com", password="pass123"
        )
        data = {
            "user": {
                "username": "anotheruser",
                "email": "dup@example.com",
                "password": "pass456",
            }
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "email",
            response.data["user"] if "user" in response.data else response.data,
        )


class UserFollowAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="follower", email="follower@example.com", password="testpass"
        )
        self.other_user = CustomUser.objects.create_user(
            username="followed", email="followed@example.com", password="testpass2"
        )
        self.login_url = f"{API_PREFIX}/users/login/"
        self.follow_url = f"{API_PREFIX}/profiles/{self.other_user.username}/follow/"

    def authenticate(self):
        login_data = {"user": {"email": self.user.email, "password": "testpass"}}
        response = self.client.post(self.login_url, login_data, format="json")
        token = response.data["user"]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_follow_requires_auth(self):
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_follow_user_success(self):
        self.authenticate()
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.other_user.followers.filter(pk=self.user.pk).exists())
        self.assertEqual(response.data["profile"]["username"], self.other_user.username)
        self.assertTrue(response.data["profile"]["following"])

    def test_unfollow_user_success(self):
        self.authenticate()
        # Follow first
        self.client.post(self.follow_url)
        # Unfollow
        response = self.client.delete(self.follow_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.other_user.followers.filter(pk=self.user.pk).exists())
        self.assertEqual(response.data["profile"]["username"], self.other_user.username)
        self.assertFalse(response.data["profile"]["following"])

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


class CurrentUserViewTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="jane",
            password="testpass123",
            first_name="Jane",
            last_name="Doe",
            street="123 Main St",
            region="Port Louis",
        )

    def test_requires_authentication(self):
        url = reverse("current-user")
        response = self.client.get(url)

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_returns_current_user_profile(self):
        logged_in = self.client.login(username="jane", password="testpass123")
        self.assertTrue(logged_in)

        url = reverse("current-user")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["first_name"], "Jane")
        self.assertEqual(data["last_name"], "Doe")
        self.assertEqual(data["street"], "123 Main St")
        self.assertEqual(data["region"], "Port Louis")

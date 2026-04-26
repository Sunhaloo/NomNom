from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Order
from delivery.models import Delivery


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


class OrderApiTests(APITestCase):
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

    def test_order_detail_includes_delivery(self):
        self.assertTrue(self.client.login(username="jane", password="testpass123"))

        order = Order.objects.create(
            user=self.user,
            order_status="Paid",
            total_amount="12.50",
        )
        delivery = Delivery.objects.create(
            order=order,
            address="123 Main St, Port Louis",
            date=timezone.now().date(),
            status="Pending",
        )

        url = reverse("order-detail", args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("delivery", data)
        self.assertIsInstance(data["delivery"], dict)
        self.assertEqual(data["delivery"]["id"], delivery.id)
        self.assertEqual(data["delivery"]["address"], "123 Main St, Port Louis")

    def test_order_list_status_filter_case_insensitive(self):
        self.assertTrue(self.client.login(username="jane", password="testpass123"))

        Order.objects.create(
            user=self.user,
            order_status="Paid",
            total_amount="10.00",
        )
        Order.objects.create(
            user=self.user,
            order_status="Pending",
            total_amount="9.00",
        )

        url = reverse("order-list")
        response = self.client.get(f"{url}?status=paid")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = response.json()
        items = payload.get("results", payload) if isinstance(payload, dict) else payload

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["order_status"], "Paid")


class DeliveryConfirmWithPhotoTests(APITestCase):
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
        self.order = Order.objects.create(
            user=self.user,
            order_status="Paid",
            total_amount="12.50",
        )

    def test_confirm_with_photo_accepts_photo_key(self):
        self.assertTrue(self.client.login(username="jane", password="testpass123"))

        delivery = Delivery.objects.create(
            order=self.order,
            address="123 Main St, Port Louis",
            date=timezone.now().date(),
            status="Pending",
        )

        url = reverse("delivery-confirm-with-photo", args=[delivery.id])
        upload = SimpleUploadedFile("proof.jpg", b"fake-image-bytes", content_type="image/jpeg")
        response = self.client.post(url, data={"photo": upload}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json().get("success"))

        delivery.refresh_from_db()
        self.assertEqual(delivery.status, "Done")
        self.assertIsNotNone(delivery.confirmed_at)
        self.assertTrue(delivery.confirmation_photo)

    def test_confirm_with_photo_accepts_confirmation_photo_key(self):
        self.assertTrue(self.client.login(username="jane", password="testpass123"))

        delivery = Delivery.objects.create(
            order=self.order,
            address="123 Main St, Port Louis",
            date=timezone.now().date(),
            status="Pending",
        )

        url = reverse("delivery-confirm-with-photo", args=[delivery.id])
        upload = SimpleUploadedFile("proof.jpg", b"fake-image-bytes", content_type="image/jpeg")
        response = self.client.post(
            url,
            data={"confirmation_photo": upload},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json().get("success"))

        delivery.refresh_from_db()
        self.assertEqual(delivery.status, "Done")
        self.assertIsNotNone(delivery.confirmed_at)
        self.assertTrue(delivery.confirmation_photo)


class TokenAuthTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="jane",
            password="testpass123",
            email="jane@example.com",
            first_name="Jane",
            last_name="Doe",
            street="123 Main St",
            region="Port Louis",
        )

    def test_token_auth_accepts_email_as_username(self):
        url = reverse("api-token-auth")
        response = self.client.post(
            url,
            data={"username": "jane@example.com", "password": "testpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertTrue(payload.get("success"))
        self.assertTrue(payload.get("data", {}).get("token"))

    def test_token_auth_invalid_credentials_returns_message(self):
        url = reverse("api-token-auth")
        response = self.client.post(
            url,
            data={"username": "jane", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        payload = response.json()
        self.assertFalse(payload.get("success"))
        self.assertEqual(payload.get("message"), "Invalid credentials")

    def test_token_auth_missing_fields_returns_message(self):
        url = reverse("api-token-auth")
        response = self.client.post(url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        payload = response.json()
        self.assertFalse(payload.get("success"))
        self.assertEqual(payload.get("message"), "Username and password are required")

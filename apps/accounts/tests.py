from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.accounts.models import Merchant, WebhookEndpoint


class AccountAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='merchant@example.com',
            email='merchant@example.com',
            password='strong-pass-123',
        )
        self.merchant = Merchant.objects.create(
            user=self.user,
            company_name='Acme Logistics',
        )

    def test_token_response_includes_profile(self):
        response = self.client.post(
            '/api/token/',
            {'email': 'merchant@example.com', 'password': 'strong-pass-123'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['profile']['merchant']['company_name'], 'Acme Logistics')

    def test_authenticated_user_can_register_webhook(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            '/api/accounts/webhooks/',
            {'url': 'https://example.com/webhook', 'events': ['SHIPMENT_CREATED']},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(WebhookEndpoint.objects.count(), 1)
        self.assertEqual(WebhookEndpoint.objects.get().merchant, self.merchant)

import re
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.utils.http import urlsafe_base64_decode
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
        self.assertEqual(response.data['dashboard_url'], '/api/analytics/dashboard/')
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_home_redirects_logged_in_merchant_to_merchant_dashboard(self):
        self.client.force_login(self.user)

        response = self.client.get('/')

        self.assertRedirects(response, '/api/analytics/dashboard/')

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


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class MerchantPasswordResetTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.merchant_user = User.objects.create_user(
            username='merchant-reset@example.com',
            email='merchant-reset@example.com',
            password='strong-pass-123',
            role=User.ROLE_MERCHANT,
            is_merchant=True,
        )
        self.merchant = Merchant.objects.create(
            user=self.merchant_user,
            company_name='Reset Logistics',
        )
        self.customer_user = User.objects.create_user(
            username='customer-reset@example.com',
            email='customer-reset@example.com',
            password='strong-pass-123',
            role=User.ROLE_CUSTOMER,
            is_merchant=False,
        )

    def test_valid_merchant_email_sends_reset_email(self):
        response = self.client.post(
            '/api/accounts/password-reset/',
            {'email': self.merchant_user.email},
        )

        self.assertRedirects(response, '/api/accounts/password-reset/done/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.merchant_user.email])
        self.assertIn('Reset your TrackFlow password', mail.outbox[0].subject)

    def test_invalid_email_displays_merchant_validation_error(self):
        response = self.client.post(
            '/api/accounts/password-reset/',
            {'email': 'unknown@example.com'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No merchant account found with this email address.',
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_customer_email_is_not_allowed_for_merchant_password_reset(self):
        response = self.client.post(
            '/api/accounts/password-reset/',
            {'email': self.customer_user.email},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'No merchant account found with this email address.',
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_email_delivery_failure_is_logged(self):
        with patch(
            'apps.accounts.forms.EmailMultiAlternatives.send',
            side_effect=Exception('SMTP unavailable'),
        ), self.assertLogs('apps.accounts.forms', level='ERROR') as logs:
            response = self.client.post(
                '/api/accounts/password-reset/',
                {'email': self.merchant_user.email},
            )

        self.assertRedirects(response, '/api/accounts/password-reset/done/')
        self.assertTrue(
            any(
                'Failed to send merchant password reset email' in message
                for message in logs.output
            )
        )

    def test_password_reset_email_contains_valid_token(self):
        self.client.post(
            '/api/accounts/password-reset/',
            {'email': self.merchant_user.email},
        )

        body = mail.outbox[0].body
        match = re.search(
            r'/api/accounts/reset/(?P<uidb64>[^/]+)/(?P<token>[^/]+)/',
            body,
        )
        self.assertIsNotNone(match)

        user_id = urlsafe_base64_decode(
            match.group('uidb64')
        ).decode()
        self.assertEqual(str(self.merchant_user.pk), user_id)
        self.assertTrue(
            default_token_generator.check_token(
                self.merchant_user,
                match.group('token'),
            )
        )

from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class SignupEmailVerificationTests(TestCase):
	@patch('accounts.views.create_and_send_otp', side_effect=RuntimeError('SMTP unavailable'))
	def test_failed_otp_delivery_rolls_back_account(self, send_otp):
		response = self.client.post(
			reverse('signup'),
			{
				'first_name': 'Ada',
				'last_name': 'Lovelace',
				'email': 'ada@example.com',
				'password': 'StrongPass123!',
				'confirm_password': 'StrongPass123!',
				'terms': 'on',
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(User.objects.filter(email='ada@example.com').exists())
		send_otp.assert_called_once_with('ada@example.com', '127.0.0.1')

	@patch('accounts.views.create_and_send_otp')
	def test_signup_redirects_to_email_confirmation(self, send_otp):
		response = self.client.post(
			reverse('signup'),
			{
				'first_name': 'Ada',
				'last_name': 'Lovelace',
				'email': 'ada@example.com',
				'password': 'StrongPass123!',
				'confirm_password': 'StrongPass123!',
				'terms': 'on',
			},
		)

		self.assertRedirects(response, reverse('verify_signup_otp'))
		confirmation = self.client.get(reverse('verify_signup_otp'))
		self.assertContains(confirmation, 'We sent a 6-digit OTP to')
		self.assertFalse(User.objects.get(email='ada@example.com').is_active)
		send_otp.assert_called_once_with('ada@example.com', '127.0.0.1')

	@patch('accounts.views.verify_otp', return_value=(True, 'OTP verified successfully.'))
	def test_signup_otp_activates_account(self, verify):
		user = User.objects.create_user(
			username='ada@example.com',
			email='ada@example.com',
			password='StrongPass123!',
			is_active=False,
		)
		session = self.client.session
		session['signup_email'] = user.email
		session.save()

		response = self.client.post(
			reverse('verify_signup_otp'),
			{'otp': '123456'},
		)

		self.assertRedirects(response, reverse('signin'))
		self.assertTrue(User.objects.get(pk=user.pk).is_active)
		verify.assert_called_once_with(user.email, '123456')

# Create your tests here.

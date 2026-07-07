from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class UsersViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass123'
        self.email = 'testuser@example.com'
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_view_post_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_already_exists(self):
        response = self.client.post(reverse('register'), {
            'username': self.username,
            'email': 'different@example.com',
            'password': 'newpassword123'
        })
        self.assertRedirects(response, reverse('register'))

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_view_post_success(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_view_post_failure(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertRedirects(response, reverse('login'))

    def test_logout_view(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_dashboard_unauthorized(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f'/login/?next={reverse("dashboard")}')

    def test_dashboard_authorized(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/dashboard.html')
        self.assertIn('total_habits', response.context)
        self.assertIn('completed_habits', response.context)
        self.assertIn('total_journals', response.context)
        self.assertIn('total_reflections', response.context)
        self.assertIn('top_streak', response.context)

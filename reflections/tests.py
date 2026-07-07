from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import DailyReflection, WeeklyReport
from unittest.mock import patch, MagicMock
import datetime
import json

class ReflectionsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.reflection = DailyReflection.objects.create(
            user=self.user,
            emotion='happy',
            activity='worked',
            affirmation="You brought joy to everything you did today 🌟"
        )

    def test_reflection_list_view(self):
        response = self.client.get(reverse('reflection_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reflections/reflection_list.html')
        self.assertContains(response, 'happy')
        self.assertContains(response, 'worked')

    def test_reflection_create_view_get(self):
        response = self.client.get(reverse('reflection_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reflections/reflection_create.html')

    def test_reflection_create_view_post(self):
        response = self.client.post(reverse('reflection_create'), {
            'emotion': 'calm',
            'activity': 'rested'
        })
        # It should redirect to reflection_result for the newly created reflection
        new_reflection = DailyReflection.objects.filter(user=self.user, emotion='calm', activity='rested').first()
        self.assertIsNotNone(new_reflection)
        self.assertRedirects(response, reverse('reflection_result', kwargs={'pk': new_reflection.pk}))
        # Verify correct custom affirmation mapping
        self.assertEqual(new_reflection.affirmation, "Rest and calm are the foundation of everything good 🌙")

    def test_reflection_result_view(self):
        response = self.client.get(reverse('reflection_result', kwargs={'pk': self.reflection.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reflections/reflection_result.html')
        self.assertContains(response, "You brought joy to everything you did today 🌟")

    @patch('reflections.views.groq.Groq')
    def test_weekly_report_view_post_success(self, mock_groq):
        # We need mood or journal entry logged for weekly report to work
        # Set up groq mock
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="Mocked weekly report patterns, insights, suggestions"))
        ]

        response = self.client.post(reverse('weekly_report'))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('report', response_data)
        self.assertTrue(WeeklyReport.objects.filter(user=self.user).exists())

    def test_weekly_report_view_post_no_data(self):
        # Delete reflections to trigger no data error
        DailyReflection.objects.all().delete()
        response = self.client.post(reverse('weekly_report'))
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import JournalEntry, AIConversation
from unittest.mock import patch, MagicMock
import json

class JournalViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.entry = JournalEntry.objects.create(user=self.user, content='Today was a good day.')

    def test_journal_list_view(self):
        response = self.client.get(reverse('journal_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'journal/journal_list.html')
        self.assertContains(response, 'Today was a good day.')

    def test_journal_create_view_get(self):
        response = self.client.get(reverse('journal_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'journal/journal_create.html')

    def test_journal_create_view_post(self):
        response = self.client.post(reverse('journal_create'), {
            'content': 'Another journal entry.'
        })
        self.assertRedirects(response, reverse('journal_list'))
        self.assertTrue(JournalEntry.objects.filter(user=self.user, content='Another journal entry.').exists())

    def test_journal_delete_view(self):
        response = self.client.post(reverse('journal_delete', kwargs={'pk': self.entry.pk}))
        self.assertRedirects(response, reverse('journal_list'))
        self.assertFalse(JournalEntry.objects.filter(pk=self.entry.pk).exists())

    @patch('journal.views.groq.Groq')
    def test_journal_chat_view_post(self, mock_groq):
        # Set up mock response
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="Empathetic mock response"))
        ]

        response = self.client.post(
            reverse('journal_chat', kwargs={'pk': self.entry.pk}),
            data=json.dumps({'message': 'How can I stay positive?'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['response'], "Empathetic mock response")
        self.assertTrue(AIConversation.objects.filter(
            journal_entry=self.entry,
            user_message='How can I stay positive?',
            ai_response='Empathetic mock response'
        ).exists())

    def test_journal_chat_view_get(self):
        response = self.client.get(reverse('journal_chat', kwargs={'pk': self.entry.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'journal/journal_chat.html')
        self.assertIn('entry', response.context)
        self.assertIn('conversations', response.context)

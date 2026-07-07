from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Habit, HabitLog
import datetime

class HabitsViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        self.habit = Habit.objects.create(user=self.user, habit_name='Drink Water')

    def test_habit_list_view(self):
        response = self.client.get(reverse('habit_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'habits/habit_list.html')
        self.assertContains(response, 'Drink Water')

    def test_habit_create_view_get(self):
        response = self.client.get(reverse('habit_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'habits/habit_create.html')

    def test_habit_create_view_post(self):
        response = self.client.post(reverse('habit_create'), {
            'habit_name': 'Read a book'
        })
        self.assertRedirects(response, reverse('habit_list'))
        self.assertTrue(Habit.objects.filter(user=self.user, habit_name='Read a book').exists())

    def test_habit_complete_view(self):
        response = self.client.post(reverse('habit_complete', kwargs={'pk': self.habit.pk}))
        self.assertRedirects(response, reverse('habit_list'))
        self.habit.refresh_from_db()
        self.assertTrue(self.habit.is_completed)
        self.assertEqual(self.habit.streak_count, 1)
        self.assertEqual(self.habit.last_completed_date, timezone.now().date())
        self.assertTrue(HabitLog.objects.filter(habit=self.habit, completed_on=timezone.now().date()).exists())

    def test_habit_delete_view(self):
        response = self.client.post(reverse('habit_delete', kwargs={'pk': self.habit.pk}))
        self.assertRedirects(response, reverse('habit_list'))
        self.assertFalse(Habit.objects.filter(pk=self.habit.pk).exists())

    def test_check_and_reset_method_yesterday(self):
        # Habit completed yesterday should be reset
        self.habit.is_completed = True
        self.habit.last_completed_date = timezone.now().date() - datetime.timedelta(days=1)
        self.habit.save()

        self.habit.check_and_reset()
        self.assertFalse(self.habit.is_completed)

    def test_check_and_reset_method_today(self):
        # Habit completed today should NOT be reset
        self.habit.is_completed = True
        self.habit.last_completed_date = timezone.now().date()
        self.habit.save()

        self.habit.check_and_reset()
        self.assertTrue(self.habit.is_completed)

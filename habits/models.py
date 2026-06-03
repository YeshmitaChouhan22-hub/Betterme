from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    habit_name = models.CharField(max_length=100)
    streak_count = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    last_completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def check_and_reset(self):
        today = timezone.now().date()
        if self.last_completed_date and self.last_completed_date < today:
            self.is_completed = False
            self.save()

    def __str__(self):
        return self.habit_name


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    completed_on = models.DateField()

    class Meta:
        unique_together = ('habit', 'completed_on')

    def __str__(self):
        return f"{self.habit.habit_name} — {self.completed_on}"
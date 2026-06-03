from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from habits.models import Habit
from journal.models import JournalEntry
from reflections.models import DailyReflection
from django.utils import timezone
import datetime

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Account created! Please login.')
        return redirect('login')
    return render(request, 'users/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    return render(request, 'users/home.html')

@login_required
def dashboard_view(request):
    from habits.models import Habit, HabitLog
    from journal.models import JournalEntry
    from reflections.models import DailyReflection
    import datetime

    habits = Habit.objects.filter(user=request.user)
    journals = JournalEntry.objects.filter(user=request.user)
    reflections = DailyReflection.objects.filter(user=request.user)

    total_habits = habits.count()
    completed_habits = habits.filter(is_completed=True).count()
    total_journals = journals.count()
    total_reflections = reflections.count()
    top_streak = max([h.streak_count for h in habits], default=0)

    mood_counts = {}
    for r in reflections:
        mood_counts[r.emotion] = mood_counts.get(r.emotion, 0) + 1
    mood_labels = list(mood_counts.keys())
    mood_data = list(mood_counts.values())

    today = timezone.now().date()
    last_7_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    day_labels = [d.strftime('%a') for d in last_7_days]

    consistency_data = []
    for day in last_7_days:
        if total_habits == 0:
            consistency_data.append(0)
        else:
            completed_count = HabitLog.objects.filter(
                habit__user=request.user,
                completed_on=day
            ).count()
            percentage = round((completed_count / total_habits) * 100)
            consistency_data.append(percentage)

    emotion_by_date = {}
    for r in reflections:
        date_str = r.created_at.strftime('%Y-%m-%d')
        emotion_by_date[date_str] = r.emotion

    journal_by_date = {}
    for j in journals:
        date_str = j.created_at.strftime('%Y-%m-%d')
        journal_by_date[date_str] = j.content[:200]

    context = {
        'total_habits': total_habits,
        'completed_habits': completed_habits,
        'total_journals': total_journals,
        'total_reflections': total_reflections,
        'top_streak': top_streak,
        'mood_labels': mood_labels,
        'mood_data': mood_data,
        'day_labels': day_labels,
        'consistency_data': consistency_data,
        'emotion_by_date': emotion_by_date,
        'journal_by_date': journal_by_date,
    }
    return render(request, 'users/dashboard.html', context)
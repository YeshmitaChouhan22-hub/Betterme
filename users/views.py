from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from habits.models import Habit
from journal.models import JournalEntry
from reflections.models import DailyReflection

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
            return redirect('home')
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

    habit_labels = [h.habit_name for h in habits]
    habit_streaks = [h.streak_count for h in habits]

    context = {
        'total_habits': total_habits,
        'completed_habits': completed_habits,
        'total_journals': total_journals,
        'total_reflections': total_reflections,
        'top_streak': top_streak,
        'mood_labels': mood_labels,
        'mood_data': mood_data,
        'habit_labels': habit_labels,
        'habit_streaks': habit_streaks,
    }
    return render(request, 'users/dashboard.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Habit, HabitLog

@login_required
def habit_list(request):
    habits = Habit.objects.filter(user=request.user)
    for habit in habits:
        habit.check_and_reset()
    return render(request, 'habits/habit_list.html', {'habits': habits})

@login_required
def habit_create(request):
    if request.method == 'POST':
        habit_name = request.POST['habit_name']
        Habit.objects.create(user=request.user, habit_name=habit_name)
        return redirect('habit_list')
    return render(request, 'habits/habit_create.html')

@login_required
def habit_complete(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = timezone.now().date()
    if not habit.is_completed:
        habit.is_completed = True
        habit.streak_count += 1
        habit.last_completed_date = today
        habit.save()
        HabitLog.objects.get_or_create(habit=habit, completed_on=today)
    return redirect('habit_list')

@login_required
def habit_delete(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    habit.delete()
    return redirect('habit_list')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Habit

@login_required
def habit_list(request):
    habits = Habit.objects.filter(user=request.user)
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
    habit.is_completed = True
    habit.streak_count += 1
    habit.save()
    return redirect('habit_list')

@login_required
def habit_delete(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    habit.delete()
    return redirect('habit_list')
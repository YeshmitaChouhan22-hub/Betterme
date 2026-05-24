from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DailyReflection

AFFIRMATIONS = {
    ('happy', 'worked'): "Amazing! You were productive and joyful today 🌟",
    ('happy', 'exercised'): "You moved your body and felt great doing it 💪",
    ('happy', 'studied'): "Learning with a happy heart is the best way to grow 📚",
    ('stressed', 'worked'): "You handled a challenging day with strength 💙",
    ('stressed', 'studied'): "Pushing through stress to learn shows real courage 🌱",
    ('stressed', 'rested'): "Rest is exactly what a stressed mind needs 🌿",
    ('tired', 'worked'): "You gave your best even when it was hard. That matters 💙",
    ('tired', 'rested'): "Rest is productive. Your body needed this 🌙",
    ('motivated', 'exercised'): "Your energy and drive today are unstoppable 🔥",
    ('motivated', 'studied'): "Motivation plus effort equals unstoppable growth 🚀",
    ('calm', 'self_care'): "Taking care of yourself with a calm mind is beautiful 🌸",
    ('calm', 'rested'): "Peace and rest together restore your soul 🌿",
    ('peaceful', 'watched_movies'): "You gave yourself permission to relax. Well done 🎬",
    ('relaxed', 'socialized'): "Connection and ease make for a perfect day 😊",
}

DEFAULT_AFFIRMATION = "Every day you show up for yourself is a victory 🌟"

@login_required
def reflection_list(request):
    reflections = DailyReflection.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'reflections/reflection_list.html', {'reflections': reflections})

@login_required
def reflection_create(request):
    if request.method == 'POST':
        emotion = request.POST['emotion']
        activity = request.POST['activity']
        affirmation = AFFIRMATIONS.get((emotion, activity), DEFAULT_AFFIRMATION)
        DailyReflection.objects.create(
            user=request.user,
            emotion=emotion,
            activity=activity,
            affirmation=affirmation
        )
        return redirect('reflection_list')
    return render(request, 'reflections/reflection_create.html')
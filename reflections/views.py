from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DailyReflection

AFFIRMATIONS = {
    ('happy', 'worked'): "You brought joy to everything you did today 🌟",
    ('happy', 'studied'): "Learning with a happy heart is the best way to grow 📚",
    ('happy', 'exercised'): "You moved your body and felt great doing it 💪",
    ('happy', 'rested'): "You gave yourself permission to be happy and at peace 🌸",
    ('happy', 'watched_movies'): "Joy and relaxation together — a perfect day 🎬",
    ('happy', 'socialized'): "Your happiness is contagious. People love being around you 😊",
    ('happy', 'self_care'): "Taking care of yourself with a joyful heart is beautiful 🌸",
    ('calm', 'worked'): "Working with a calm mind means your best work came out today 🌿",
    ('calm', 'studied'): "A calm mind absorbs knowledge deeply. Well done 📖",
    ('calm', 'exercised'): "Peace and movement together create true balance 🧘",
    ('calm', 'rested'): "Rest and calm are the foundation of everything good 🌙",
    ('calm', 'watched_movies'): "You gave your mind a calm and gentle break today 🎬",
    ('calm', 'socialized'): "Your calm presence is a gift to everyone around you 💙",
    ('calm', 'self_care'): "Taking care of yourself with a calm mind is beautiful 🌸",
    ('stressed', 'worked'): "You handled a challenging day with real strength 💙",
    ('stressed', 'studied'): "Pushing through stress to learn shows incredible courage 🌱",
    ('stressed', 'exercised'): "Using movement to release stress — that is wisdom 💪",
    ('stressed', 'rested'): "Rest is exactly what a stressed mind and body needed 🌿",
    ('stressed', 'watched_movies'): "Taking a break when stressed is not giving up — it is self-care 💙",
    ('stressed', 'socialized'): "Reaching out when stressed takes courage. You did well 🤝",
    ('stressed', 'self_care'): "Choosing yourself on a hard day is the bravest thing 🌸",
    ('motivated', 'worked'): "Your drive today moved mountains. Keep going 🚀",
    ('motivated', 'studied'): "Motivation plus effort equals unstoppable growth 📚",
    ('motivated', 'exercised'): "Your energy and drive today are truly unstoppable 🔥",
    ('motivated', 'rested'): "Even motivated people need rest. You chose wisely 🌙",
    ('motivated', 'watched_movies'): "Recharging your motivated mind — smart move 🎬",
    ('motivated', 'socialized'): "Your motivated energy inspires everyone around you ✨",
    ('motivated', 'self_care'): "A motivated mind in a cared-for body is unstoppable 💪",
    ('tired', 'worked'): "You showed up even when it was hard. That is everything 💙",
    ('tired', 'studied'): "Studying while tired shows how seriously you take your growth 📖",
    ('tired', 'exercised'): "Moving your body even when tired — that is dedication 💪",
    ('tired', 'rested'): "Rest is productive. Your body needed exactly this 🌙",
    ('tired', 'watched_movies'): "Your mind needed softness today and you gave it that 🎬",
    ('tired', 'socialized'): "Connecting with others even when tired — you gave a lot today 🤝",
    ('tired', 'self_care'): "Tired but still choosing yourself. That is real self-love 🌸",
    ('peaceful', 'worked'): "Working from a place of peace creates your best results 🌿",
    ('peaceful', 'studied'): "A peaceful mind is the best learning environment 📚",
    ('peaceful', 'exercised'): "Movement and peace together — your body thanks you 🧘",
    ('peaceful', 'rested'): "Peace and rest together restore the soul completely 🌙",
    ('peaceful', 'watched_movies'): "A peaceful evening well spent 🎬",
    ('peaceful', 'socialized'): "Your peaceful presence made everyone around you feel safe 💙",
    ('peaceful', 'self_care'): "Peace plus self-care equals a full and beautiful day 🌸",
    ('emotional', 'worked'): "Working through emotions takes real strength. Be proud 💙",
    ('emotional', 'studied'): "Even on emotional days you kept going. That matters so much 📖",
    ('emotional', 'exercised'): "Movement is one of the best ways to process emotions 💪",
    ('emotional', 'rested'): "Giving yourself rest on an emotional day is wisdom 🌙",
    ('emotional', 'watched_movies'): "Sometimes we need stories to help us feel our feelings 🎬",
    ('emotional', 'socialized'): "Letting others in on emotional days is a sign of strength 🤝",
    ('emotional', 'self_care'): "On emotional days, choosing yourself is the most important thing 🌸",
    ('relaxed', 'worked'): "Working while relaxed — that is the dream state 🌿",
    ('relaxed', 'studied'): "Relaxed learning is the most effective kind 📚",
    ('relaxed', 'exercised'): "Effortless movement on a relaxed day — beautiful 🧘",
    ('relaxed', 'rested'): "Full relaxation — your mind and body both say thank you 🌙",
    ('relaxed', 'watched_movies'): "The perfect relaxed evening. You deserved every minute 🎬",
    ('relaxed', 'socialized'): "Easy connection and ease make for a perfect day 😊",
    ('relaxed', 'self_care'): "Relaxed and cared for — you are glowing from the inside 🌸",
}

DEFAULT_AFFIRMATION = "Every single day you show up for yourself is a victory 🌟"

@login_required
def reflection_list(request):
    reflections = DailyReflection.objects.filter(
        user=request.user).order_by('-created_at')
    return render(request, 'reflections/reflection_list.html',
                  {'reflections': reflections})

@login_required
def reflection_create(request):
    if request.method == 'POST':
        emotion = request.POST['emotion']
        activity = request.POST['activity']
        affirmation = AFFIRMATIONS.get(
            (emotion, activity), DEFAULT_AFFIRMATION)
        reflection = DailyReflection.objects.create(
            user=request.user,
            emotion=emotion,
            activity=activity,
            affirmation=affirmation
        )
        return redirect('reflection_result', pk=reflection.pk)
    return render(request, 'reflections/reflection_create.html')

@login_required
def reflection_result(request, pk):
    reflection = DailyReflection.objects.get(pk=pk, user=request.user)
    return render(request, 'reflections/reflection_result.html',
                  {'reflection': reflection})
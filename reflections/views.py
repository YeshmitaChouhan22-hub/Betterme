from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from .models import DailyReflection, WeeklyReport
from journal.models import JournalEntry
from habits.models import Habit
import httpx
import groq
import datetime

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


def generate_weekly_report(user):
    today = timezone.now().date()
    week_start = today - datetime.timedelta(days=7)

    reflections = DailyReflection.objects.filter(
        user=user,
        created_at__date__gte=week_start
    )
    journals = JournalEntry.objects.filter(
        user=user,
        created_at__date__gte=week_start
    )
    habits = Habit.objects.filter(user=user)

    reflection_summary = ""
    for r in reflections:
        reflection_summary += f"- Felt {r.emotion}, activity: {r.activity} on {r.created_at.strftime('%A')}\n"

    journal_summary = ""
    for j in journals:
        journal_summary += f"- {j.created_at.strftime('%A')}: {j.content[:200]}...\n"

    habit_summary = ""
    for h in habits:
        habit_summary += f"- {h.habit_name}: {h.streak_count} day streak, completed: {h.is_completed}\n"

    if not reflection_summary and not journal_summary:
        return None

    prompt = f"""You are an empathetic AI wellness analyst for an app called BetterMe.

Analyse this user's past 7 days of data and write a warm, personal weekly report.

MOOD AND ACTIVITY LOG:
{reflection_summary if reflection_summary else "No reflections logged this week."}

JOURNAL ENTRIES:
{journal_summary if journal_summary else "No journal entries this week."}

HABIT TRACKING:
{habit_summary if habit_summary else "No habits tracked."}

Write a weekly report with exactly these 3 sections:

1. PATTERNS THIS WEEK
Identify 2-3 emotional or behavioural patterns you notice. Be specific and warm.

2. WHAT THIS TELLS US
What do these patterns reveal about this person's current life situation? Be insightful and empathetic.

3. THREE SUGGESTIONS FOR NEXT WEEK
Give 3 specific, actionable, personalised suggestions based on the data. Not generic advice — make it specific to what you see.

Keep the entire report under 300 words. Write directly to the user using "you". Be warm, encouraging, and never clinical."""

    client = groq.Groq(
        api_key=settings.GROQ_API_KEY,
        http_client=httpx.Client(verify=False)
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7,
    )

    import re
    report_text = response.choices[0].message.content
    report_text = re.sub(r'#{1,3}\s*', '', report_text)
    report_text = re.sub(r'\*\*(.*?)\*\*', r'\1', report_text)
    report_text = report_text.strip()

    WeeklyReport.objects.create(
        user=user,
        report_text=report_text,
        week_start=week_start,
        week_end=today
    )

    return report_text


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


@login_required
def weekly_report(request):
    from django.utils import timezone
    import datetime

    WeeklyReport.objects.filter(
        user=request.user,
        created_at__lt=timezone.now() - datetime.timedelta(hours=24)
    ).delete()

    past_reports = WeeklyReport.objects.filter(
        user=request.user).order_by('-created_at')

    if request.method == 'POST':
        report_text = generate_weekly_report(request.user)
        if report_text is None:
            return JsonResponse({
                'error': 'Not enough data yet. Log some moods and journal entries first!'
            }, status=400)
        return JsonResponse({'report': report_text})

    return render(request, 'reflections/weekly_report.html', {
        'past_reports': past_reports
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JournalEntry, AIConversation
from django.conf import settings
import json
import groq

def get_ai_response(journal_content, conversation_history, user_message):
    import httpx
    client = groq.Groq(
    api_key=settings.GROQ_API_KEY,
    http_client=httpx.Client(verify=False)
    )

    system_prompt = f"""You are a warm, empathetic, and thoughtful journaling companion for an app called BetterMe. 

The user has written the following journal entry:

---
{journal_content}
---

Your role is to:
- Read their entry with care and respond with genuine empathy
- Ask thoughtful follow-up questions to help them reflect deeper
- Never judge, never give harsh advice
- Keep responses conversational and warm — like a supportive friend
- Keep responses concise — 2 to 4 sentences maximum
- Focus on emotional understanding, not solutions unless asked

Remember: this is a safe space for the user."""

    messages = [{"role": "system", "content": system_prompt}]

    for conv in conversation_history:
        messages.append({"role": "user", "content": conv.user_message})
        messages.append({"role": "assistant", "content": conv.ai_response})

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=300,
        temperature=0.8,
    )

    return response.choices[0].message.content


@login_required
def journal_list(request):
    entries = JournalEntry.objects.filter(
        user=request.user).order_by('-created_at')
    return render(request, 'journal/journal_list.html', {'entries': entries})


@login_required
def journal_create(request):
    if request.method == 'POST':
        content = request.POST['content']
        JournalEntry.objects.create(user=request.user, content=content)
        return redirect('journal_list')
    return render(request, 'journal/journal_create.html')


@login_required
def journal_delete(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    entry.delete()
    return redirect('journal_list')


@login_required
def journal_chat(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    conversations = AIConversation.objects.filter(
        journal_entry=entry).order_by('created_at')

    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')

        if not user_message.strip():
            return JsonResponse({'error': 'Empty message'}, status=400)

        ai_response = get_ai_response(
            entry.content,
            conversations,
            user_message
        )

        AIConversation.objects.create(
            journal_entry=entry,
            user_message=user_message,
            ai_response=ai_response
        )

        return JsonResponse({'response': ai_response})

    return render(request, 'journal/journal_chat.html', {
        'entry': entry,
        'conversations': conversations
    })
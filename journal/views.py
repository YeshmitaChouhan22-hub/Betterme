from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JournalEntry

@login_required
def journal_list(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')
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
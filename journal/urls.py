from django.urls import path
from . import views

urlpatterns = [
    path('journal/', views.journal_list, name='journal_list'),
    path('journal/create/', views.journal_create, name='journal_create'),
    path('journal/delete/<int:pk>/', views.journal_delete, name='journal_delete'),
    path('journal/chat/<int:pk>/', views.journal_chat, name='journal_chat'),
]
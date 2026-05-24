from django.urls import path
from . import views

urlpatterns = [
    path('habits/', views.habit_list, name='habit_list'),
    path('habits/create/', views.habit_create, name='habit_create'),
    path('habits/complete/<int:pk>/', views.habit_complete, name='habit_complete'),
    path('habits/delete/<int:pk>/', views.habit_delete, name='habit_delete'),
]
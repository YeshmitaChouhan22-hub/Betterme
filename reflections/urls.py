from django.urls import path
from . import views

urlpatterns = [
    path('reflections/', views.reflection_list, name='reflection_list'),
    path('reflections/create/', views.reflection_create, name='reflection_create'),
]
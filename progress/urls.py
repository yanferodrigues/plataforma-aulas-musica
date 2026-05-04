from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('', views.progress, name='progress'),
    path('update/', views.update_progress, name='update'),
    path('exercise/submit/', views.submit_exercise, name='submit_exercise'),
]

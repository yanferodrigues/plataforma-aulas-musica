from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('modules/', views.module_list, name='module_list'),
    path('modules/<int:pk>/', views.module_detail, name='module_detail'),
    path('modules/<int:module_pk>/lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('modules/<int:module_pk>/lessons/<int:pk>/comunidade/', views.lesson_qa, name='lesson_qa'),
]

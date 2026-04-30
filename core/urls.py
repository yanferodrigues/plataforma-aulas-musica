from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),

    # Studio — painel superusuário
    path('studio/', views.studio, name='studio'),

    path('studio/modulos/novo/', views.studio_module_save, name='studio_module_create'),
    path('studio/modulos/<int:pk>/editar/', views.studio_module_save, name='studio_module_edit'),
    path('studio/modulos/<int:pk>/excluir/', views.studio_module_delete, name='studio_module_delete'),

    path('studio/aulas/nova/', views.studio_lesson_save, name='studio_lesson_create'),
    path('studio/aulas/<int:pk>/editar/', views.studio_lesson_save, name='studio_lesson_edit'),
    path('studio/aulas/<int:pk>/excluir/', views.studio_lesson_delete, name='studio_lesson_delete'),

    path('studio/conquistas/nova/', views.studio_achievement_save, name='studio_achievement_create'),
    path('studio/conquistas/<int:pk>/editar/', views.studio_achievement_save, name='studio_achievement_edit'),
    path('studio/conquistas/<int:pk>/excluir/', views.studio_achievement_delete, name='studio_achievement_delete'),

    path('studio/materiais/novo/', views.studio_material_save, name='studio_material_create'),
    path('studio/materiais/<int:pk>/editar/', views.studio_material_save, name='studio_material_edit'),
    path('studio/materiais/<int:pk>/excluir/', views.studio_material_delete, name='studio_material_delete'),

    path('studio/exercicios/novo/', views.studio_exercise_save, name='studio_exercise_create'),
    path('studio/exercicios/<int:pk>/editar/', views.studio_exercise_save, name='studio_exercise_edit'),
    path('studio/exercicios/<int:pk>/excluir/', views.studio_exercise_delete, name='studio_exercise_delete'),

    path('studio/usuarios/<int:pk>/excluir/', views.studio_user_delete, name='studio_user_delete'),
]

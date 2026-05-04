from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('password/reset/', views.password_reset, name='password_reset'),
    path('senha/solicitar/', views.request_password_change, name='request_password_change'),
    path('senha/confirmar/<uidb64>/<token>/', views.confirm_password_change, name='confirm_password_change'),

    # OAuth
    path('google/login/', views.google_login, name='google_login'),
    path('google/callback/', views.google_callback, name='google_callback'),

    path('notifications/', views.notifications_api, name='notifications_api'),
    path('avatar/', views.avatar_upload, name='avatar_upload'),
    path('settings/save/', views.save_settings, name='save_settings'),
]

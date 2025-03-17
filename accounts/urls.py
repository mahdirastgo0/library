from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'
urlpatterns = [
    path("register/", views.register, name="register"),
    path('login/', views.user_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/<str:email>/', views.profile, name='profile'),
    path('verify-email/<str:token>/', views.verify_email, name='verify-email'),
    path('resend-verification/<str:email>/', views.resend_verification, name='resend_verification'),
    path('password-reset/', auth_views.PasswordResetView.as_view, name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view,
         name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view, name='password_reset_complete'),
]

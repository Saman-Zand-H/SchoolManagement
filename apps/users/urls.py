from django.urls import path

from . import views

urlpatterns = [
    path('logout/', views.logout_view, name="logout"),
    path('profile/', views.profile_view, name="profile"),
    path('password-change/', views.custom_password_change_view, name="change-password"),
]

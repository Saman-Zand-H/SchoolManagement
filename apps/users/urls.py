from django.urls import path

from . import views

urlpatterns = [
    path('logout/', views.logout_view, name="logout"),
    path("phonenumber/", views.add_phonenumber_view, name="phonenumber"),
    path("verify-phonenumber/",
         views.phonenumber_verification_view,
         name="verify_phonenumber"),
]

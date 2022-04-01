from django.urls import path

from . import views


app_name = "messenger"

urlpatterns = [
    path("", views.chats_list_view, name="conversations-list"),
    path("<str:group_id>/", views.chat_page_view, name="chat-page"),
    path("<str:group_id>/members", views.members_view, name="manage-members"),
]
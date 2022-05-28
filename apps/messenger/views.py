from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.db.models import Q 
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from functools import partial
from logging import getLogger
import json

from .models import ChatGroup, Member
from .forms import GroupForm, MembersForm, ConversationForm


logger = getLogger(__name__)


class ChatsListView(LoginRequiredMixin, View):
    context = dict()
    template_name = "dashboard/messenger/chats_list.html"
        
    def get(self, *args, **kwargs):
        memberships = self.request.user.member_user.all()
        loadTemplate = self.request.path.split()[-1]
        is_support = self.request.user.has_perm("supports.support")
        self.context.update({
            "nav_color": "bg-dark",
            "memberships": memberships,
            "segment": loadTemplate,
            "is_support": is_support,
            "algolia_application_id": settings.ALGOLIA_APPLICATION_ID,
            "algolia_search_key": settings.ALGOLIA_SEARCH_KEY,
            "school_name": self.request.user.school.name,
        })
        if is_support:
            self.context["group_form"] = GroupForm()
        return render(self.request, 
                      self.template_name, 
                      self.context)

    def post(self, *args, **kwargs):
        conversation_form = ConversationForm(self.request.POST)
        success_message = partial(messages.success, 
                                  request=self.request)
        error_message = partial(messages.error, 
                                request=self.request)
        if conversation_form.is_valid():
            conversation_type = conversation_form.cleaned_data.get(
                "conversation_type")
            match conversation_type:
                case "group":
                    if self.request.user.has_perm("supports.support"):
                        form = GroupForm(self.request.POST, self.request.FILES)
                        if form.is_valid():
                            form = form.save(commit=False)
                            form.owner = self.request.user
                            form.is_pm = False
                            form.save()
                            group = get_object_or_404(
                                ChatGroup, group_id=form.group_id)
                            Member.objects.create(
                                user=self.request.user, 
                                chatgroup=group,
                            )
                            success_message(
                                message="Group created successfully.")
                            return redirect("messenger:chat-page", 
                                            group_id=group.group_id)
                        error_message(
                            message="Invalid input provided.")
                        return render(self.request, 
                                      self.template_name, 
                                      self.context)
                    raise PermissionDenied()
                case "pm":
                    target_user = get_object_or_404(
                        get_user_model(), 
                        username=conversation_form.cleaned_data.get(
                            "target_user"),
                    )
                    chatgroup, created = ChatGroup.objects.get_or_create(
                        group_id=f"{self.request.user.username}_{target_user.username}",
                        is_pm=True,
                    )
                    if created:
                        Member.objects.get_or_create(user=self.request.user, 
                                                     chatgroup=chatgroup)
                        Member.objects.get_or_create(user=target_user, 
                                                     chatgroup=chatgroup)
                        notification_gn = f"notification_{target_user.username}"
                        channel_layer = get_channel_layer()
                        notif_data = {
                            "body": "You have been added to this conversation",
                            "chatgroup_id": chatgroup.group_id,
                            "date_written": datetime.now().strftime("%a"),
                            "chatgroup_url": chatgroup.get_absolute_url(),
                            "group_name": self.request.user.name,
                            "group_picture_url": self.request.user.get_picture_url,
                            "unread_messages_count": self.request.user.member_user.unread_message.count()
                        }
                        async_to_sync(channel_layer.group_send)(
                            notification_gn,
                            {
                                "type": "notify.message",
                                "message": notif_data
                            }
                        )
                        success_message(message="Conversation created successfully.")
                    return redirect("messenger:chat-page", 
                                    group_id=chatgroup.group_id)
                case _:
                    error_message(message="Invalid parameter provided.")
        self.context["form"] = conversation_form
        error_message(message="Invalid input provided.")
        return render(self.request, self.template_name, self.context)
        
    
    
chats_list_view = ChatsListView.as_view()


class ChatPageView(LoginRequiredMixin, View):
    template_name = "dashboard/messenger/chat_page.html"
    context = dict()
        
    def get(self, *args, **kwargs):
        loadTemplate = self.request.path.split()[-1]
        chatgroup_qs = ChatGroup.objects.filter(
            group_id=self.kwargs.get("group_id"))
        if chatgroup_qs.exists():
            chatgroup = chatgroup_qs.first()
            other_user = None
            # If the room is a private message room, show the other
            # endpoint user's bio 
            if chatgroup.is_pm:
                other_user = chatgroup.member_chatgroup.exclude(
                    user=self.request.user).first().user.about
            last_message_qs = chatgroup.ordered_messages.filter(
                seen=False)
            self.context.update({
                "nav_color": "bg-dark",
                "segment": loadTemplate,
                "chatgroup": chatgroup,
                "last_message_qs": last_message_qs,
                "group_form": GroupForm(instance=chatgroup),
                "algolia_search_key": settings.ALGOLIA_SEARCH_KEY,
                "algolia_application_id": settings.ALGOLIA_APPLICATION_ID,
                "school_name": self.request.user.school.name,
                "other_user_about": other_user,
            })
            return render(self.request, 
                        self.template_name, 
                        self.context)
        return redirect("messenger:home")
    
    def post(self, *args, **kwargs):
        error_message = partial(messages.error, 
        request=self.request)
        success_message = partial(messages.success, 
        request=self.request)
        chatgroup = get_object_or_404(ChatGroup, 
                                      group_id=self.kwargs.get("group_id"))
        if chatgroup in self.request.user.owned_groups:
            form = GroupForm(self.request.POST, 
                             self.request.FILES, 
                             instance=chatgroup)
            if form.is_valid():
                form.save()
                success_message(
                    message="Group updated successfully")
            else:
                error_message(
                    message="invalid inputs provided.")
            return redirect("messenger:chat-page", 
                            group_id=chatgroup.group_id)
        raise PermissionDenied("The use is not the owner of this group.")
   
   
chat_page_view = ChatPageView.as_view()


class MembersView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        error_message = partial(messages.error, 
                                request=self.request)
        success_message = partial(messages.success, 
                                request=self.request)
        form = MembersForm(self.request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("member")
            request_type = form.cleaned_data.get("request_type")
            user = get_object_or_404(get_user_model(), 
                                     username=username)
            chatgroup = get_object_or_404(ChatGroup, 
                                          group_id=self.kwargs.get("group_id"))
            match request_type:
                case "add":
                    instance, created = Member.objects.get_or_create(
                        user=user, chatgroup=chatgroup)
                    channel_layer = get_channel_layer()
                    notif_data = {
                        "body": "You have been added to this group",
                        "chatgroup_id": chatgroup.group_id,
                        "date_written": datetime.now().strftime("%a"),
                        "chatgroup_url": chatgroup.get_absolute_url(),
                        "group_name": chatgroup.get_name(self.request.user),
                        "group_picture_url": chatgroup.get_picture(self.request.user),
                    }
                    async_to_sync(channel_layer.group_send)(
                        f"notification_{username}",
                        {
                            "type": "notify.message",
                            "message": json.dumps(notif_data)
                        }
                    )
                    if created:
                        success_message(
                            message="User added successfully.")
                case "delete":
                    member_qs = Member.objects.filter(user=user, 
                                                      chatgroup=chatgroup)
                    # Merely delete the member instance if the user is not the 
                    # owner. If the user is the owner, delete the group
                    if member_qs.exists():
                        member_qs.delete()
                        success_message(
                            message="Member deleted successfully.")
                    else:
                        error_message(
                            message="This user isn't a member of this group.")
                case "leave":
                    member_qs = Member.objects.filter(Q(user=user) &
                                                      Q(chatgroup=chatgroup))
                    if member_qs.exists():
                        member_qs.delete()
                        if self.request.user == chatgroup.owner:
                            chatgroup.delete()
                            success_message(
                                message="Group deleted successfully.")
                        else:
                            member_qs.delete()
                            success_message(
                                message="You left the group successfully.")
                    else:
                        error_message(
                            message="This user isn't a member of this group.")
                    return redirect("messenger:home")
                case _:
                    error_message(message="Invalid parameter provided.")
        else:
            error_message(message="Invalid inputs provided.")
        return redirect("messenger:chat-page", group_id=kwargs.get("group_id"))
                

members_view = MembersView.as_view()

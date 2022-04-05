from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.conf import settings

from functools import partial
from logging import getLogger

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
            "school_name": self.request.user.school_name[0],
        })
        if is_support:
            self.context["group_form"] = GroupForm()
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        conversation_form = ConversationForm(self.request.POST)
        success_message = partial(messages.success, request=self.request)
        error_message = partial(messages.error, request=self.request)
        if conversation_form.is_valid():
            conversation_type = conversation_form.cleaned_data.get("conversation_type")
            match conversation_type:
                case "group":
                    if self.request.user.has_perm("supports.support"):
                        form = GroupForm(self.request.POST, self.request.FILES)
                        if form.is_valid():
                            form = form.save(commit=False)
                            group_id = form.group_id
                            form.owner = self.request.user
                            form.is_pm = False
                            form.save()
                            Member.objects.create(
                                user=self.request.user, 
                                chatgroup=ChatGroup.objects.get(group_id=group_id),
                            )
                            success_message(message=_("Group created successfully"))
                            return redirect("messenger:chat-page", group_id=group_id)
                        error_message(message=_("Invalid input provided."))
                        return render(self.request, self.template_name, self.context)
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
                        Member.objects.get_or_create(user=target_user, chatgroup=chatgroup)
                        success_message(message=_("Conversation created successfully."))
                    return redirect("messenger:chat-page", group_id=chatgroup.group_id)
        error_message(message=_("Invalid input provided."))
        return render(self.request, self.template_name, self.context)
        
    
    
chats_list_view = ChatsListView.as_view()


class ChatPageView(LoginRequiredMixin, View):
    template_name = "dashboard/messenger/chat_page.html"
    context = dict()
        
    def get(self, *args, **kwargs):
        loadTemplate = self.request.path.split()[-1]
        chatgroup = ChatGroup.objects.get(group_id=self.kwargs["group_id"])
        other_user = None
        # if the room is a private message room, show the other
        # endpoint's bio 
        if chatgroup.is_pm:
            other_user = chatgroup.member_chatgroup.exclude(
                user=self.request.user).first().user.about
        last_message = chatgroup.ordered_messages.filter(
            seen=False).last()
        self.context.update({
            "nav_color": "bg-dark",
            "segment": loadTemplate,
            "chatgroup": chatgroup,
            "last_message": last_message,
            "group_form": GroupForm(instance=chatgroup),
            "algolia_search_key": settings.ALGOLIA_SEARCH_KEY,
            "algolia_application_id": settings.ALGOLIA_APPLICATION_ID,
            "school_name": self.request.user.school_name[0],
            "other_user_about": other_user,
        })
        return render(self.request, self.template_name, self.context)
    
    def post(self, *args, **kwargs):
        error_message = partial(messages.error, request=self.request)
        success_message = partial(messages.success, request=self.request)
        chatgroup = get_object_or_404(ChatGroup, group_id=self.kwargs["group_id"])
        if chatgroup in self.request.user.owned_groups:
            form = GroupForm(self.request.POST, self.request.FILES, instance=chatgroup)
            if form.is_valid():
                form.save()
                success_message(message=_("Group updated successfully"))
            else:
                error_message(message=_("invalid inputs provided."))
            return redirect("messenger:chat-page", group_id=chatgroup.group_id)
        raise PermissionDenied("The use is not the owner of this group.")
   
   
chat_page_view = ChatPageView.as_view()


class MembersView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        error_message = partial(messages.error, request=self.request)
        success_message = partial(messages.success, request=self.request)
        form = MembersForm(self.request.POST)
        if form.is_valid():
            username = form.cleaned_data["member"]
            request_type = form.cleaned_data["request_type"]
            user = get_object_or_404(get_user_model(), 
                                     username=username)
            chatgroup = get_object_or_404(ChatGroup, 
                                          group_id=self.kwargs["group_id"])
            match request_type:
                case "add":
                    instance, created = Member.objects.get_or_create(
                        user=user, chatgroup=chatgroup)
                    if created:
                        success_message(message=_("User added successfully."))
                case "delete":
                    member_qs = Member.objects.filter(user=user, chatgroup=chatgroup)
                    # Merely delete the member instance if the user is not the 
                    # owner. If the user is the owner, delete the group
                    if member_qs.exists():
                        member_qs.delete()
                        success_message(message=_("Member deleted successfully."))
                    else:
                        error_message(message=_("This user isn't a member of this group.")) 
                case "leave":
                    member_qs = Member.objects.filter(user=user, chatgroup=chatgroup)
                    if member_qs.exists():
                        member_qs.delete()
                        if self.request.user == chatgroup.owner:
                            chatgroup.delete()
                            success_message(message=_("Group deleted successfully."))
                        else:
                            success_message(message=_("You left the group successfully."))
                    else:
                        error_message(message=_("This user isn't a member of this group."))
                    return redirect("messenger:conversations-list")
        else:
            error_message(message=_("Invalid inputs provided."))
        return redirect("messenger:chat-page", group_id=kwargs["group_id"])
                

members_view = MembersView.as_view()

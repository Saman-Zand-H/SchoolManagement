from django.contrib import admin

from .models import ChatGroup, Member, Message


@admin.action(description="mark as read".title())
def mark_as_read(modeladmin, request, queryset):
    queryset.update(seen=True)
    

@admin.action(description="mark as unread".title())
def mark_as_unread(modeladmin, request, queryset):
    queryset.update(seen=False)


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "group_id", "owner", "is_pm")
    search_fields = ("name", "group_id")
    
    
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("user", "chatgroup", "date_joined")
    search_fields = ("user", "chatgroup")
    
    
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "message_id",
        "author", 
        "chatgroup", 
        "body", 
        "date_written",
        "seen",
    ]
    admin_order_field = "-date_written"
    search_fields = ("author", "chatgroup", "body", "message_id")
    list_filter = ("author", "chatgroup", "seen")
    actions = [
        mark_as_read,
        mark_as_unread,
    ]
        
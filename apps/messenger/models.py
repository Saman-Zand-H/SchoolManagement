from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db import IntegrityError

from string import ascii_letters
from random import choices
from uuid import uuid4

from users.models import validate_file_size, validate_file_extension


def generate_group_id(length=12):
    return "".join(choices(ascii_letters, k=length))


class ChatGroup(models.Model):
    name = models.CharField(max_length=100, 
                            blank=True, 
                            null=True)
    photo = models.ImageField(
        upload_to="media",
        default="empty-profile.jpg",        
        blank=True,
        validators=[validate_file_size, validate_file_extension],
    )
    bio = models.TextField(blank=True, null=True)
    group_id = models.CharField(max_length=41, 
                                unique=True, 
                                default=generate_group_id)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chatgroup_owner",
        null=True,
        blank=True,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    is_pm = models.BooleanField(default=True)
    
    def __str__(self):
        if self.is_pm:
            return f"private message: {self.name}"
        return f"{self.name} - Owner: {self.owner.username}"
    
    def get_absolute_url(self):
        return reverse("messenger:chat-page", kwargs={"group_id": self.group_id})
    
    def ordered_messages(self):
        return self.message_chatgroup.order_by("date_written")
    
    def get_name(self, user):
        members = self.member_chatgroup.all()
        if self.is_pm:
            the_other_member = [*filter(lambda member: member.user != user, members)][0]
            return the_other_member.user.name()
        else:
            return self.name
    
    def get_picture(self, user):
        members = self.member_chatgroup.all()
        if self.is_pm:
            the_other_member = [*filter(lambda member: member.user != user, members)][0]
            return the_other_member.user.picture
        else:
            return self.photo
        
    def is_marked_as_unread(self):
        if self.message_chatgroup.filter(seen=False).exists():
            return True
        return
    
    
class Member(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_user",
    )
    chatgroup = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
        related_name="member_chatgroup",
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.chatgroup}"
    
    def save(self, *args, **kwargs):
        chatgroup = ChatGroup.objects.get(group_id=self.chatgroup.group_id)
        if chatgroup.is_pm and chatgroup.member_chatgroup.count()>=2:
            raise IntegrityError("A private message can only have two members")
        super().save(*args, **kwargs)
        
    
    class Meta:
        unique_together = (
            ("user", "chatgroup"),
        )
            
    
class Message(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="message_author",
    )
    chatgroup = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
        related_name="message_chatgroup",
    )
    message_id = models.UUIDField(
        default=uuid4,
        primary_key=True,
        editable=False,
        unique=True,
    )
    body = models.TextField()
    seen = models.BooleanField(default=False)
    date_written = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.author} - {self.chatgroup}: {self.body[:10]}..."
        
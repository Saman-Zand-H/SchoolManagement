from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.db.models import Q
from webpush import send_user_notification
import json
from typing import List, Tuple
import logging
from uuid import UUID

from messenger.models import ChatGroup, Message, Member

logger = logging.getLogger(__name__)


class MessengerConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
        self.user = self.scope["user"]
        self.user_distinct_group = f"activity_{self.user.username}_{self.group_id}"
        
        self.chatgroup = await self.get_chatgroup(self.group_id)
        if self.chatgroup is not None:            
            if self.chatgroup.is_pm:
                self.group_name = self.group_id
            else:
                self.group_name = f"group_{self.group_id}"
            await self.channel_layer.group_add(
                self.user_distinct_group,
                self.channel_name
            )
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name,
            )
            await self.send({
                "type": "websocket.accept",
            })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )
        await self.channel_layer.group_discard(
            self.user_distinct_group,
            self.channel_name,
        )
        raise StopConsumer()

    async def websocket_receive(self, event):
        text_data = event.get("text")
        if text_data is not None:
            text_data_json = json.loads(text_data)
            message_type = text_data_json["type"]
            match message_type:
                case "msg":
                    chatgroup = await self.get_chatgroup(self.group_id)
                    if chatgroup is not None:
                        message = await self.create_message(
                            text_data_json["body"],
                            chatgroup,
                        )
                        text_data_json.update({
                            "sender": self.user.name,
                            "sender_username": self.user.username,
                            "type": "msg",
                            "message_id": message.message_id.hex,
                            "date_written": message.date_written.strftime(
                                "%B %d, %Y, %I:%M %p"),
                        })
                        await self.channel_layer.group_send(
                            self.group_name, 
                            {
                                "type": "chat_message",
                                "message": text_data_json,
                            },
                        )
                        usernames = await self.get_all_members(chatgroup)
                        for username in usernames:
                            notif_group_name = f"notification_{username[0]}"
                            notification_group_name = notif_group_name
                            unread_messages = await self.get_unread_messages(username[0])
                            notif_data = {
                                "body": text_data_json.get("body")[:30],
                                "chatgroup_id": self.group_id,
                                "date_written": message.date_written.strftime("%a"),
                                "chatgroup_url": chatgroup.get_absolute_url(),
                                "group_name": self.user.name,
                                "group_picture_url": self.user.get_picture_url,
                                "unread_messages_count": unread_messages,
                            }
                            await self.channel_layer.group_send(
                                notification_group_name,
                                {
                                    "type": "notify.message",
                                    "message": notif_data,
                                }
                            )
                case "seen":
                    msg_id = text_data_json["message_id"]
                    msg_sender = text_data_json["sender"]
                    sender_distinct_group = f"activity_{msg_sender}_{self.group_id}"
                    
                    text_data_json["message_ids"] = await self.mark_message_as_read(msg_id)
                    
                    await self.channel_layer.group_send(
                        sender_distinct_group,
                        {
                            "type": "chat_message",
                            "message": text_data_json,
                        },
                    )

    async def chat_message(self, event):
        message_id = event["message"]["message_id"]
        username = self.scope["user"].username   
        await self.set_last_read_message(username, message_id)
        await self.send(
            {
                "type": "websocket.send",
                "text": json.dumps(event["message"]),
            }
        )
        
    @database_sync_to_async
    def get_chatgroup(self, group_id: str):
        try:
            return ChatGroup.objects.get(group_id=group_id)
        except ChatGroup.DoesNotExist:
            return
        
    @database_sync_to_async
    def get_unread_messages(self, username: str):
        membership = Member.objects.filter(user__username=username)
        return membership.last().unread_messages.count() if membership.exists() else 0
        
    @database_sync_to_async
    def get_all_members(self, chatgroup: ChatGroup) -> List[Tuple[str, ]]:
        return list(chatgroup.member_chatgroup.values_list("user__username"))

    @database_sync_to_async
    def create_message(self, message: str, chatgroup: ChatGroup | int):
        return Message.objects.create(author=self.user,
                                      body=message,
                                      chatgroup=chatgroup)
        
    @database_sync_to_async
    def set_last_read_message(self, username:str, message_id:str) -> int:
        return Member.objects.filter(user__username=username).update(
            last_read_message=UUID(message_id))

    @database_sync_to_async
    def mark_message_as_read(self, message_id: str) -> List[str]:
        try:
            message = Message.objects.get(
                message_id=UUID(message_id))
            messages_qs = Message.objects.filter(
                Q(date_written__lte=message.date_written) & Q(seen=False))
            messages_qs_ids = [message.message_id.hex for message in messages_qs]
            messages_qs.update(seen=True)
            return messages_qs_ids
        except Message.DoesNotExist:
            pass


messenger_consumer = MessengerConsumer.as_asgi()


class NotificationConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.group_name = f"notification_{self.username}"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,    
        )
        await self.send({
            "type": "websocket.accept",
        })    
        
    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )
        raise StopConsumer()
    
    async def notify_message(self, event):
        user = self.scope["user"]
        group_name = event["message"].get("group_name")
        chatgroup_url = event["message"].get("chatgroup_url")
        message = event["message"].get("body")
        payload = {
            'head': "Takhte Whiteboard",
            'body': f"{group_name}: {message}",
            'icon': "/static/assets/img/brand/favicon.png",
            'url': chatgroup_url,
        }
        await self.send(
            {
                "type": "websocket.send",
                "text": json.dumps(event["message"]),
            }
        )
        await sync_to_async(send_user_notification)(
            user=user,
            payload=payload,
            ttl=10,
        )


notification_consumer = NotificationConsumer.as_asgi()

from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async

import json
import logging
from uuid import UUID

from messenger.models import ChatGroup, Message, Member

logger = logging.getLogger(__name__)


class MessengerConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
        self.sender = self.scope["user"]
        self.user_distinct_group = f"activity_{self.sender.username}_{self.group_id}"
        
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
                    message = await self.create_message(
                        text_data_json["body"],
                        chatgroup,
                    )
                    text_data_json.update({
                        "sender": self.sender.name(),
                        "sender_username": self.sender.username,
                        "type": "msg",
                        "message_id": message.message_id.hex,
                        "date_written": message.date_written.strftime("%B %d, %Y, %I:%M %p"),
                    })
                    await self.channel_layer.group_send(
                        self.group_name, 
                        {
                            "type": "chat_message",
                            "message": text_data_json,
                        },
                    )
                case "seen":
                    msg_id = text_data_json["message_id"]
                    msg_sender = text_data_json["sender"]
                    sender_distinct_group = f"activity_{msg_sender}_{self.group_id}"
                    
                    text_data_json["message_ids"] = await self.mark_message_as_read(msg_id)
                    await self.set_last_read_message(msg_sender, msg_id)
                    await self.set_last_read_message(self.sender, msg_id)
                    
                    await self.channel_layer.group_send(
                        sender_distinct_group,
                        {
                            "type": "chat_message",
                            "message": text_data_json,
                        },
                    )

    async def chat_message(self, event):
        message_id = event["message"]["message_id"]
        await self.set_last_read_message(
            self.scope["user"].username, message_id)
        await self.send(
            {
                "type": "websocket.send",
                "text": json.dumps(event["message"]),
            })

    @database_sync_to_async
    def get_chatgroup(self, group_id):
        try:
            return ChatGroup.objects.get(group_id=group_id)
        except ChatGroup.DoesNotExist:
            return

    @database_sync_to_async
    def create_message(self, message, chatgroup):
        return Message.objects.create(author=self.sender,
                                      body=message,
                                      chatgroup=chatgroup)
        
    @database_sync_to_async
    def set_last_read_message(self, username, message_id):
        return Member.objects.filter(user__username=username).update(
            last_read_message=UUID(message_id))

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        try:
            message = Message.objects.get(
                message_id=UUID(message_id.strip()))
            messages_qs = Message.objects.filter(
                date_written__lte=message.date_written, seen=False)
            messages_qs_ids = [message.message_id.hex for message in messages_qs]
            messages_qs.update(seen=True)
            return messages_qs_ids
        except Message.DoesNotExist:
            pass


messenger_consumer = MessengerConsumer.as_asgi()

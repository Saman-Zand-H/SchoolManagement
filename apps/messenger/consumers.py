from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async

import json
import logging
from uuid import UUID

from messenger.models import ChatGroup, Message

logger = logging.getLogger(__name__)


class MessengerConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
        self.sender = self.scope["user"]
        self.user_distinct_group = f"activity_{self.sender.username}_{self.group_id}"
        
        self.chatgroup = await self.get_chatgroup(self.group_id)
        if self.chatgroup is not None:            
            if self.chatgroup.is_pm:
                self.group_name = f"{self.sender.username}_{self.group_id}"
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
                        "channel_name": self.channel_name,
                        "type": "msg",
                        "message_id": message.message_id.hex,
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
                    logger.error(msg_id)
                    msg_sender = text_data_json["sender"]
                    logger.error(f"socket received a request to mark message as seen a message by {msg_sender}")
                    sender_distinct_group = f"activity_{msg_sender}_{self.group_id}"
                    
                    await self.mark_message_as_read(msg_id)
                    await self.channel_layer.group_send(
                        sender_distinct_group,
                        {
                            "type": "chat_activity",
                            "message": text_data_json,
                        },
                    )

    async def chat_message(self, event):
        await self.send(
            {
                "type": "websocket.send",
                "text": json.dumps(event["message"]),
            })

    async def chat_activity(self, event):
        await self.send({
            "type": "websocket.send",
            "text": json.dumps(event["message"])
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
    def mark_message_as_read(self, message_id):
        try:
            message = Message.objects.get(
                message_id=UUID(message_id.strip()))
            Message.objects.filter(
                date_written__lte=message.date_written).update(seen=True)
        except Message.DoesNotExist:
            pass


messenger_consumer = MessengerConsumer.as_asgi()

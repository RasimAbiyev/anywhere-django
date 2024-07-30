# Messenger. Sockets. Chat logic.
import json
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    message_data = {}
    user_interactions = {}

    async def connect(self):
        self.roomGroupName = "group_chat_gfg"
        self.user = self.scope['user']
        await self.channel_layer.group_add(
            self.roomGroupName,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get("action")
        message = text_data_json.get("message")
        messageId = text_data_json.get("messageId")
        username = text_data_json.get("username")
        user_id = self.user.id
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if action == 'send':
            self.message_data[messageId] = {'like': 0, 'dislike': 0}
            self.user_interactions[messageId] = {'liked': False, 'disliked': False}
            await self.channel_layer.group_send(
                self.roomGroupName,
                {
                    "type": "sendMessage",
                    "message": message,
                    "username": username,
                    "messageId": messageId,
                    "likeCount": self.message_data[messageId]['like'],
                    "dislikeCount": self.message_data[messageId]['dislike'],
                    "userHasLiked": False,
                    "userHasDisliked": False,
                    "timestamp": timestamp
                }
            )
        elif action in ('toggleLike', 'toggleDislike'):
            user_has_interacted = False
            if action == 'toggleLike':
                if self.user_interactions[messageId]['liked']:
                    self.message_data[messageId]['like'] -= 1
                    self.user_interactions[messageId]['liked'] = False
                else:
                    if self.user_interactions[messageId]['disliked']:
                        self.message_data[messageId]['dislike'] -= 1
                        self.user_interactions[messageId]['disliked'] = False
                    self.message_data[messageId]['like'] += 1
                    self.user_interactions[messageId]['liked'] = True
                user_has_interacted = True
            elif action == 'toggleDislike':
                if self.user_interactions[messageId]['disliked']:
                    self.message_data[messageId]['dislike'] -= 1
                    self.user_interactions[messageId]['disliked'] = False
                else:
                    if self.user_interactions[messageId]['liked']:
                        self.message_data[messageId]['like'] -= 1
                        self.user_interactions[messageId]['liked'] = False
                    self.message_data[messageId]['dislike'] += 1
                    self.user_interactions[messageId]['disliked'] = True
                user_has_interacted = True

            await self.channel_layer.group_send(
                self.roomGroupName,
                {
                    "type": "updateCounts",
                    "messageId": messageId,
                    "likeCount": self.message_data[messageId]['like'],
                    "dislikeCount": self.message_data[messageId]['dislike'],
                    "userHasLiked": self.user_interactions[messageId]['liked'],
                    "userHasDisliked": self.user_interactions[messageId]['disliked']
                }
            )
        elif action == 'delete':
            if messageId in self.message_data:
                del self.message_data[messageId]
                del self.user_interactions[messageId]
            await self.channel_layer.group_send(
                self.roomGroupName,
                {
                    "type": "deleteMessage",
                    "messageId": messageId
                }
            )

    async def sendMessage(self, event):
        message = event["message"]
        username = event["username"]
        messageId = event["messageId"]
        likeCount = event["likeCount"]
        dislikeCount = event["dislikeCount"]
        timestamp = event["timestamp"]
        await self.send(text_data=json.dumps({
            "action": "send",
            "message": message,
            "username": username,
            "messageId": messageId,
            "likeCount": likeCount,
            "dislikeCount": dislikeCount,
            "userHasLiked": False,
            "userHasDisliked": False,
            "timestamp": timestamp
        }))

    async def deleteMessage(self, event):
        messageId = event["messageId"]
        await self.send(text_data=json.dumps({
            "action": "delete",
            "messageId": messageId
        }))

    async def updateCounts(self, event):
        messageId = event["messageId"]
        likeCount = event["likeCount"]
        dislikeCount = event["dislikeCount"]
        userHasLiked = event["userHasLiked"]
        userHasDisliked = event["userHasDisliked"]
        await self.send(text_data=json.dumps({
            "action": "update",
            "messageId": messageId,
            "likeCount": likeCount,
            "dislikeCount": dislikeCount,
            "userHasLiked": userHasLiked,
            "userHasDisliked": userHasDisliked
        }))
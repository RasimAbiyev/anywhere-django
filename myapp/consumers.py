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
            if messageId not in self.user_interactions:
                self.user_interactions[messageId] = {}
            self.user_interactions[messageId][user_id] = {'liked': False, 'disliked': False}
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
            if messageId not in self.user_interactions:
                self.user_interactions[messageId] = {}
            if user_id not in self.user_interactions[messageId]:
                self.user_interactions[messageId][user_id] = {'liked': False, 'disliked': False}

            user_interaction = self.user_interactions[messageId][user_id]

            if action == 'toggleLike':
                if user_interaction['liked']:
                    self.message_data[messageId]['like'] -= 1
                    user_interaction['liked'] = False
                else:
                    if user_interaction['disliked']:
                        self.message_data[messageId]['dislike'] -= 1
                        user_interaction['disliked'] = False
                    self.message_data[messageId]['like'] += 1
                    user_interaction['liked'] = True
            elif action == 'toggleDislike':
                if user_interaction['disliked']:
                    self.message_data[messageId]['dislike'] -= 1
                    user_interaction['disliked'] = False
                else:
                    if user_interaction['liked']:
                        self.message_data[messageId]['like'] -= 1
                        user_interaction['liked'] = False
                    self.message_data[messageId]['dislike'] += 1
                    user_interaction['disliked'] = True

            await self.channel_layer.group_send(
                self.roomGroupName,
                {
                    "type": "updateMessage",
                    "messageId": messageId,
                    "likeCount": self.message_data[messageId]['like'],
                    "dislikeCount": self.message_data[messageId]['dislike'],
                    "userHasLiked": user_interaction['liked'],
                    "userHasDisliked": user_interaction['disliked']
                }
            )
        elif action == 'delete':
            self.message_data.pop(messageId, None)
            self.user_interactions.pop(messageId, None)
            await self.channel_layer.group_send(
                self.roomGroupName,
                {
                    "type": "deleteMessage",
                    "messageId": messageId
                }
            )

    async def sendMessage(self, event):
        await self.send(text_data=json.dumps({
            'action': 'send',
            'message': event['message'],
            'username': event['username'],
            'messageId': event['messageId'],
            'likeCount': event['likeCount'],
            'dislikeCount': event['dislikeCount'],
            'userHasLiked': event['userHasLiked'],
            'userHasDisliked': event['userHasDisliked'],
            'timestamp': event['timestamp']
        }))

    async def updateMessage(self, event):
        await self.send(text_data=json.dumps({
            'action': 'update',
            'messageId': event['messageId'],
            'likeCount': event['likeCount'],
            'dislikeCount': event['dislikeCount'],
            'userHasLiked': event['userHasLiked'],
            'userHasDisliked': event['userHasDisliked']
        }))

    async def deleteMessage(self, event):
        await self.send(text_data=json.dumps({
            'action': 'delete',
            'messageId': event['messageId']
        }))
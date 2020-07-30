import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Group
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.person_name=self.user.username 
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        #if self.user.is_authenticated:
        #if self.user.rooms.filter(pk=int(to_room_id)).exists():
         #   self.to_room = Room.objects.get(pk=int(to_room_id))
          #  self.room_name = 'room_%s' %self.to_room.id
    #else:

     #   self.close() #do something to create room for the user''''

        messages = await self.get_last_messages()
        print("messages",self.room_group_name)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        #
        #await self.channel_layer.group_send(
         #   self.room_group_name, {
          #  "type": "chat_message",
        # "message":self.person_name+" is on the chat"
        #    }
        #)

        await self.accept()

    async def disconnect(self, close_code):
        
        #await self.channel_layer.group_send(
        #    self.room_group_name, {
        #    "type": "chat_message",
        #    "message":self.person_name + " is not on the chat anymore"
        #    }
        #)

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
    
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        room_id = text_data_json['room_id']
   
        await self.save_message(message, room_id)
        print("here", User.objects.get(username = self.person_name).profile.image.url)

        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message':self.person_name+" : "+message,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'photo' : User.objects.get(username = self.person_name).profile.image.url

        }))

    @database_sync_to_async
    def get_last_messages(self):
       return Message.objects.all()
    
    @database_sync_to_async
    def save_message(self, message, room_id):
        return Message.objects.create(author = self.user, content = message, group = Group.objects.get(pk = room_id))

        
import json
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework import mixins
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from djangochannelsrestframework.observer import model_observer

from .models import Room, Message
from django.contrib.auth.models import User
from .serializers import MessageSerializer, RoomSerializer, UserSerializer
from chat import serializers


class MyConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "pk"
    
    async def connect(self):
        await self.accept()
        await self.message_activity.subscribe()
        self.__user = self.scope["user"]
    
    @model_observer(Message)
    async def message_activity(self, message:dict, action =None, **kwargs):
        try:
            users_in_room:list = message["room"]["current_users"]
            message["action"] = action
            if self.__user.id in users_in_room:
                await self.send_json(message)
        except Exception as e:
            print(e)

    @message_activity.serializer
    def message_activity(self, instance: Message, action, **kwargs):
        return MessageSerializer(instance).data
    
    @action()
    async def create_message(self, message, room_id, **kwargs):
        try:
            room: Room = await self.get_room(pk=room_id)
            if not room or not await self.check_user_in_room(room):
                return
            await database_sync_to_async(Message.objects.create)(
                room=room,
                user=self.__user,
                text=message
            )
        except Exception as e:
            print(e)
    
    @action()
    async def load_rooms(self, action=None, **kwargs):
        rooms = await self.get_all_rooms()
        data ={
            "action":action,
            "rooms":rooms
        }
        return await self.send_json(data)
     
    @database_sync_to_async   
    def get_all_rooms(self):
        rooms = Room.objects.filter(current_users__id__in = [self.__user.id])
        serializer = RoomSerializer(rooms, many=True, 
                                    remove_fields=["messages", "current_users"])
        return serializer.data
    
    @database_sync_to_async
    def check_user_in_room(self, room:Room):
        if not room:
            return
        return room.current_users.filter(id = self.__user.id).exists()
    
    @database_sync_to_async
    def get_room(self, pk: int) -> Room:
        return Room.objects.filter(pk=pk).first()
   
   

# class Test(AsyncWebsocketConsumer):
#     chat_name = "test"
    
#     async def connect(self):
#         await self.accept()
#         await self.channel_layer.group_add(self.chat_name, self.channel_name)
#         self.uid = uuid.uuid4()
#         await self.send(text_data=json.dumps(
#             {
#                 "type":"connection_established",
#                 "message":"hello in ws live!",
#                 "user_id":f"{self.uid}"
#             }))
    
#     async def receive(self, text_data=None, bytes_data=None):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#         await self.channel_layer.group_send(self.chat_name, {
#             "type":"chat_message",
#             "message":message,
#             "user_id":f"{self.uid}"
#         })

#     async def chat_message(self, event):
#         message = event["message"]
#         user_id = event["user_id"]
#         await self.send(text_data=json.dumps(
#             {
#                 "type":"message",
#                 "message":message,
#                 "user_id":user_id
#             }))
        
        
    
class UserConsumer(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.PatchModelMixin,
        mixins.UpdateModelMixin,
        mixins.CreateModelMixin,
        mixins.DeleteModelMixin,
        GenericAsyncAPIConsumer,
):

    queryset = User.objects.all()
    serializer_class = UserSerializer


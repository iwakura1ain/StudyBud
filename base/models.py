from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, SET_NULL


# Create your models here.
# python class model -> database entries


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    
class Message(models.Model):
    #parent user | delete all message models if parent is deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #parent room | delete all message models if parent is deleted
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    
    #message content 
    body = models.TextField()

    #timestamps 
    last_updated = models.DateField(auto_now=True)
    first_created = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ["-last_updated", "-first_created"]

    def __str__(self):
        return self.body[:50]

# class MessageRoom(models.Model):
#     message = models.ForeignKey(Message, on_delete=models.CASCADE)
#     room = models.ForeignKey("Room", on_delete=models.SET_NULL, null=True)


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    name = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    desc = models.TextField(null=True, blank=True)

    
    participants = models.ManyToManyField(User, related_name="participants", blank=True)
    
    last_updated = models.DateField(auto_now=True)
    first_created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-last_updated", "-first_created"]

    def __str__(self):
        return self.name 






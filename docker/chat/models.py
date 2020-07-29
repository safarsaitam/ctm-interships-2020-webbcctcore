from django.db import models
from django.contrib.auth import get_user_model
from bcctapp.models import Teams
from django.urls import reverse

class Group(models.Model):
    name = models.CharField(null=False, max_length = 64)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)

    def __str__(self):
        return "name is {} and its id is {}".format(self.name, self.team.id)
    
    def get_absolute_url(self):
        return reverse("chat:show-chat", kwargs = {'room_name':self.pk})



class Message(models.Model):
    author = models.ForeignKey(get_user_model(), related_name = 'author_messages', on_delete = models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add = True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE) 


    def __str__(self):
        return self.author.username

    



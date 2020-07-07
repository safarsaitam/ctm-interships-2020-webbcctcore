# Imports
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class CinderellaImages(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    before_image = models.FileField(upload_to='cinderella_images/before') 
    image = models.FileField(upload_to='cinderella_images/after')
    age = models.PositiveIntegerField(default=0)
    weight = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    bra_size = models.FloatField(default=0.0)
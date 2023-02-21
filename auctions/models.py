from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    userID = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=30, blank=True, null=True)
    currentHighestBid = models.FloatField(blank=True, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    image = models.ImageField(null=True, blank=True) #uploads_to= (media)


# We need the models to auto cascade when one of them is updated
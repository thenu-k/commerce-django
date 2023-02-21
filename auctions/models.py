from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=100, blank=False, null=True)
    userID = models.IntegerField(blank=False, null=True)
    username = models.CharField(max_length=100, blank=False, null=True)
    category = models.CharField(max_length=30, blank=False, null=True)
    currentHighestBid = models.IntegerField(blank=False, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True, blank=True, null=True)


# We need the models to auto cascade when one of them is updated
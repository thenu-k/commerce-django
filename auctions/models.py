from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    userID = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=30, blank=True, null=True)
    currentHighestBid = models.FloatField(blank=True, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    image = models.ImageField(null=True, blank=True) #uploads_to= (media)
    userKey = models.ForeignKey(User, on_delete=models.CASCADE)
    isClosed = models.BooleanField(auto_created=False,  blank=True, null=False)
    description = models.CharField(max_length=1000, blank=True, null=True)

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    dateCreated = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    bidValue = models.FloatField(blank=True, null=True)
    listingID = models.IntegerField(blank=True, null=True)
    createdByUserID = models.IntegerField(blank=True, null=True)
    createdByUserKey = models.ForeignKey(User, on_delete=models.CASCADE)
    listingKey = models.ForeignKey(Listing, on_delete=models.CASCADE)
    isHighest = models.BooleanField(auto_created=True, null=True, blank=True)


# We need the models to auto cascade when one of them is updated
# foreign keys will be given as IDs
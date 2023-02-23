from django.contrib import admin
from .models import Listing, User, Bid

models = [Listing, User, Bid]
admin.site.register(models)
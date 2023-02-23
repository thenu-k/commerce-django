from django.contrib import admin
from .models import Listing, User, Bid, Watch

models = [Listing, User, Bid, Watch]
admin.site.register(models)
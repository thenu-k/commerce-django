from django.contrib import admin
from .models import Listing, User

models = [Listing, User]
admin.site.register(models)
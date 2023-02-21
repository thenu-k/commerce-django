from django import forms
from .models import *

class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'username', 'userID', 'category', 'image', 'currentHighestBid']
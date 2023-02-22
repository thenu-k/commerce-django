from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Listing
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
import ast
from django.core import serializers
from .forms import *
import json

def index(request):
    listings = Listing.objects.all()
    listings = serializers.serialize('json', listings)
    return render(request, "auctions/index.html", {'listings':listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def newListingPage(request):
    if request.user.is_authenticated:
        return render(request, 'auctions/new.html')
    else: 
        return redirect('/login')

@csrf_exempt
def createListing(request): 
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        if (request.method == 'POST'):
            form = NewListingForm().save(commit=False)
            form.username = request.user.username
            form.userID = request.user.id
            form.currentHighestBid = request.POST['currentHighestBid']
            form.category = request.POST['category']
            form.title = request.POST['title']
            form.image = request.FILES['image']
            form.userKey = user
            form.save()
        return redirect('/')
    else: 
        return redirect('/login')  
        
def getAllListings(request):
    if request.method=='GET':
        data = Listing.objects.all().values()
        payload = {
            'data': list(data)
        }
        return JsonResponse(payload)

def getUserListings(request):
    if request.method=='GET':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        userID = body['userID']
        try:
            userObject = User.objects.get(id=userID)   #filter returns multiple values, so get must be used if this will be used as a key
            listings = Listing.objects.filter(userKey=userObject)
            listings_json = json.loads(serializers.serialize('json', listings))
            payload = {
                'userID': userID,
                'listings': listings_json
            }
            return JsonResponse(payload)
        except: 
            payload = {
                'userID': userID,
                'status': 'failure'
            }
            return JsonResponse(payload, status=500)
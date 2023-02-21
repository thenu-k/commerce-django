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

def index(request):
    return render(request, "auctions/index.html")


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
    # if request.user.is_authenticated:
    #     requestData = ast.literal_eval(request.body.decode('utf8'))
    #     newListing = Listing(title=requestData["title"], category=requestData['category'], username=request.user.username, userID=request.user.id, currentHighestBid=requestData['baseBid'])
    #     newListing.save()
    #     payload = {
    #         'status': 'success',
    #         'requestBody' : requestData
    #     }
    #     return JsonResponse(payload)
    # else:
    #     payload = {
    #         'status': 'failure: not logged in',
    #     }
    #     return JsonResponse(payload, status=401)
    if (request.method == 'POST'):
        form = NewListingForm().save(commit=False)
        form.username = request.user.username
        form.userID = request.user.id
        form.currentHighestBid = request.POST['currentHighestBid']
        form.category = request.POST['category']
        form.title = request.POST['title']
        form.image = request.FILES['image']
        form.save()
    return HttpResponse('yo')
            
        
def getAllListings(request):
    if request.method=='GET':
        data = Listing.objects.all().values()
        payload = {
            'data': list(data)
        }
        return JsonResponse(payload)
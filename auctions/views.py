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
from django.db.models import Max
from django.forms.models import model_to_dict

def index(request):
    # Getting the filter params if it exists
    filter = request.GET.get('filter','null')
    if(filter=='null' or filter=='all'):
        listings = Listing.objects.all()
    else:
        listings = Listing.objects.filter(category=filter)
    payload = []
    for count in range(listings.count()):
        currentListingObject = listings[count]
        #Checking whether a bid exists. If not, the base bid will be the current highest bid
        if Bid.objects.filter(listingID=currentListingObject.id ).exists():
            currentHighestBid = Bid.objects.filter(listingID=currentListingObject.id).aggregate(Max('bidValue')).get('bidValue__max')
        else:
            currentHighestBid = Listing.objects.get(id=currentListingObject.id).baseBid
        tempValue = {
            'currentHighestBid': currentHighestBid,
            #this function convert a SINGLE object to a dictionary. the default is there to conver the imagefield to string
            # 'id' : json.dumps(model_to_dict(currentListingObject), default=str)
            'id': currentListingObject.id,
            'username': currentListingObject.username,
            'imageURL': str(currentListingObject.image),
            'isClosed': currentListingObject.isClosed,
            'title': currentListingObject.title
        }
        payload.append(tempValue)
    # No closed listings should be displayed
    return render(request, "auctions/index.html", {'payload':payload, 'displayClosed': False})


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
            form.baseBid = request.POST['currentHighestBid']
            form.category = request.POST['category']
            form.title = request.POST['title']
            form.image = request.FILES['image']
            form.userKey = user
            form.isClosed = False
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
            if  User.objects.filter(id=userID).exists():
                userObject = User.objects.get(id=userID)   #filter returns multiple values, so get must be used if this will be used as a key
                listings = Listing.objects.filter(userKey=userObject)
                listings_json = json.loads(serializers.serialize('json', listings))
                payload = {
                    'userID': userID,
                    'listings': listings_json
                }
                return JsonResponse(payload)
            else: 
                payload = {
                    'status': 'user not found'
                }
                return JsonResponse(payload, status=404)
        except: 
            payload = {
                'userID': userID,
                'status': 'failure'
            }
            return JsonResponse(payload, status=500)

def renderAccountPage(request, userID):
    if  User.objects.filter(id=userID).exists():
        # Getting the filter params if it exists
        filter = request.GET.get('filter','null')
        if(filter=='null' or filter=='all'):
            listings = Listing.objects.filter(userID=userID)
        else:
            listings = Listing.objects.filter(category=filter, userID=userID)
        payload = []
        for count in range(listings.count()):
            currentListingObject = listings[count]
            #Checking whether a bid exists. If not, the base bid will be the current highest bid
            if Bid.objects.filter(listingID=currentListingObject.id ).exists():
                currentHighestBid = Bid.objects.filter(listingID=currentListingObject.id).aggregate(Max('bidValue')).get('bidValue__max')
            else:
                currentHighestBid = Listing.objects.get(id=currentListingObject.id).baseBid
            tempValue = {
                'currentHighestBid': currentHighestBid,
                #this function convert a SINGLE object to a dictionary. the default is there to conver the imagefield to string
                # 'id' : json.dumps(model_to_dict(currentListingObject), default=str)
                'id': currentListingObject.id,
                'username': currentListingObject.username,
                'imageURL': str(currentListingObject.image),
                'isClosed': currentListingObject.isClosed,
                'title': currentListingObject.title
            }
            payload.append(tempValue)
        return render(request, 'auctions/Account/account.html', {'payload': payload, 'displayClosed' : True})
    else: 
        return redirect('/404') 

@csrf_exempt
def deleteAccount(request):
    try:
        if request.user.is_authenticated:
            body = json.loads(request.body)
            userID = body['userID']
            userObject = User.objects.filter(id=userID)
            if  userObject.exists() and request.user.id==int(userID):
                userObject.delete()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'user not found'}, status=404)
        else:
            return redirect('/404')
    except:
        return JsonResponse({'status': 'server error'}, status=500)

def renderListingPage(request, listingID):
    listingObject = Listing.objects.filter(id=int(listingID)).values()
    # Checking whether this user is the user who created the listing
    userEqual = False
    if(request.user.id==listingObject[0]['userID']):
        userEqual =True
    else: 
        userEqual = False
    currentUserIsHighest = False
    #Checking whether a bid exists. If not, the base bid will be the current highest bid
    if Bid.objects.filter(listingID=listingID ).exists():
        currentHighestBid = Bid.objects.filter(listingID=listingID).aggregate(Max('bidValue')).get('bidValue__max')
        #Checking if the current user is the highest bidder
        if(request.user.id==Bid.objects.filter(listingID=listingID).values().latest('id')['createdByUserID']):
                currentUserIsHighest = True
    else:
        currentHighestBid = Listing.objects.filter(id=listingID).values('baseBid')[0]['baseBid']
    #Checking whether the user has watched this item
    userHasWatched = False
    if Watch.objects.filter(listingID=listingID, createdByUserID=request.user.id ).exists():
        userHasWatched = True
    context = {
        'listing': listingObject,
        'currentHighestBid': currentHighestBid,
        'userEqual' : userEqual,
        'currentUserIsHighest': currentUserIsHighest,
        'userHasWatched': userHasWatched
    }
    print(context)
    return render(request, 'auctions/Listing/listing.html', context)

@csrf_exempt
def newBid(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    newBidValue = body['newBidValue']
    listingID = body['listingID']
    listingObject = Listing.objects.get(id=listingID)
    userObjet = User.objects.get(id=request.user.id)
    allBidObjectsForListing = Bid.objects.filter(listingID=listingID)
    if Bid.objects.filter(listingID=listingID).exists():
        currentHighestBid = Bid.objects.filter(listingID=listingID).aggregate(Max('bidValue')).get('bidValue__max')
    else:
        currentHighestBid = Listing.objects.filter(id=listingID).values('baseBid')[0]['baseBid']
    if(newBidValue>currentHighestBid):
        #listingObject.currentHighestBid= newBidValue
        listingObject.save()
        newBidObject = Bid(bidValue = newBidValue, listingID=listingObject.id, createdByUserID=request.user.id, createdByUserKey=userObjet, listingKey=listingObject)
        newBidObject.save()
        payload = {'status': 'success'}
        return  JsonResponse(payload)
    payload = {'status': 'failure'}
    return JsonResponse(payload, status=401)

@csrf_exempt
def setWatch(request, stateRequired, listingID):
    if request.user.is_authenticated:
        if(stateRequired=='watch'):
            #Getting the objects for the key
            userObject = User.objects.get(id=request.user.id)
            listingObject = Listing.objects.get(id=listingID)
            #Creating the new object
            newWatchObject = Watch(
                listingID = listingID,
                createdByUserID = request.user.id,
                createdByUserKey = userObject,
                listingKey = listingObject,
            )
            newWatchObject.save()
            return JsonResponse({'success': 'true'})
        elif(stateRequired=='unwatch'):
            #Deleting the existing object
            watchObject = Watch.objects.get(listingID=listingID, createdByUserID=request.user.id)
            watchObject.delete()
            return JsonResponse({'success': 'true'})
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse

from .models import *


def index(request):

    active_listings = AuctionListings.objects.all()

    return render(request, "auctions/index.html",{
        'active_listings': active_listings
    })


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


def create_listing(request,user_id):

    if request.method == 'POST':
        
        title = request.POST['title']
        cat_obj = Category.objects.get_or_create(title=request.POST['category']) 
        description = request.POST['description']
        starting_bid = request.POST['starting_bid']
        image = request.FILES.get('image')
        lister = User.objects.get(id=user_id)
        listing = AuctionListings.objects.create(title=title,category=cat_obj[0],description=description,
                        starting_bid=starting_bid,image=image,lister=lister)
        return redirect('index')

    return render(request,'auctions/create_listing.html')

def listing_detail(request,pk):

    listing = AuctionListings.objects.get(pk=pk)
    return render(request,'auctions/listing_detail.html',{
        'listing': listing
    })

def categories(request):

    categories = Category.objects.all()

    return render(request,'auctions/categories.html',{
        'categories':categories
    })

def category_detail(request,pk):

    category = Category.objects.get(id=pk)
    listings = category.auctionlistings_set.all()

    return render(request,'auctions/category_detail.html',{
        'category': category,
        'listings': listings
    })

@login_required
def place_bid(request,pk):

    user = User.objects.get(id=request.user.id)
    listing = AuctionListings.objects.get(id=pk)
    print(user,listing)
    if request.method == 'POST':
        bid_price = request.POST.get('bid')
        print(bid_price)
        print(listing.highest_bid)
        if listing.highest_bid == 0 and int(bid_price) >= int(listing.starting_bid):
            listing.highest_bid = bid_price
            print('success')
            listing.save()
            bid = Bid.objects.create(bid_price=bid_price,user=user)
        elif listing.highest_bid != 0 and int(bid_price) >= int(listing.highest_bid):
            print(bid_price-listing.highest_bid)
            listing.highest_bid = bid_price
            listing.save()
            bid = Bid.objects.create(bid_price=bid_price,user=user)
        else:
            message = 'Error: Please type a number equal or greater than the highest price.'
            print(message)
            return render(request,'auctions/listing_detail.html',{'listing':listing,'message': message})
        
    return render(request,'auctions/listing_detail.html',{
        'bid': bid,
        'listing': listing
    })
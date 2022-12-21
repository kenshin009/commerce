from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
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

    categories = Category.objects.all()

    if request.method == 'POST':
        
        title = request.POST['title']
        slug = slugify(title)
        category = Category.objects.get(title=request.POST['category'])
        print(category)
        description = request.POST['description']
        starting_bid = request.POST['starting_bid']
        image = request.FILES.get('image')
        lister = User.objects.get(id=user_id)
        listing = AuctionListings.objects.create(title=title,slug=slug,category=category,description=description,
                        starting_bid=starting_bid,highest_bid=starting_bid,image=image,lister=lister)
        highest_bidder = Highest_bidder.objects.create(user=lister,listing_code=listing.slug)
        return redirect('index')    

    return render(request,'auctions/create_listing.html',{'categories':categories})

def listing_detail(request,slug):


    listing = AuctionListings.objects.get(slug=slug) 
    #to get the comments of this listing
    comments = Comment.objects.filter(session_id=listing.id)
    #to check the user is not anonymous user
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        user = None
    
    if user is None:
        return render(request,'auctions/listing_detail.html',{'listing':listing})

    #then I access the user's specific watchlist items
    #to check if this listing is present in the watchlist
    try:
        watchlist = Watchlist.objects.get(user=request.user,slug=listing.slug)
    except Watchlist.DoesNotExist:
        watchlist = None

    #check if the user is the one who created the listing
    if request.user == listing.lister:
        try:
            highest_bidder = Highest_bidder.objects.get(listing_code=listing.slug)
        except Highest_bidder.DoesNotExist:
            highest_bidder = None
        #to give permission to close the auction
        #I assign a variable to the boolean value
        check = True 

        return render(request,'auctions/listing_detail.html',{
            'watchlist': watchlist,
            'listing': listing,
            'highest_bidder': highest_bidder,
            'check': check,
            'comments': comments
        })

    else:
        pass

    return render(request,'auctions/listing_detail.html',{
        'watchlist': watchlist,
        'listing': listing,
        'comments': comments
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
    comments = Comment.objects.filter(session_id=listing.id)
    #to check if this listing is present in the watchlist
    try:
        watchlist = Watchlist.objects.get(user=request.user,slug=listing.slug)
    except Watchlist.DoesNotExist:
        watchlist = None

    if request.method == 'POST':
        bid_price = request.POST.get('bid')

        #check if bid amount is not zero and greater than the base price
        if int(bid_price) > int(listing.highest_bid):
            listing.highest_bid = bid_price
            listing.save()
            bid = Bid.objects.create(bid_price=bid_price,user=user)
            highest_bidder = Highest_bidder.objects.create(user=bid.user,listing_code=listing.slug)
            #makes the highest_bidder only one user
            highest_bidders = Highest_bidder.objects.filter(listing_code=listing.slug)
            highest_bidders.first().delete()

        else:
            error = 'Error: Please type a number greater than the highest price.'
    
            return render(request,'auctions/listing_detail.html',{
                'listing':listing,
                'error': error,
                'comments': comments,
                'watchlist': watchlist
            })
        
        return render(request,'auctions/listing_detail.html',{
            'highest_bidder': highest_bidder,
            'bid': bid,
            'listing': listing,
            'comments': comments,
            'watchlist': watchlist
        })
        
    return redirect(reverse('listing_detail',args=(listing.slug,)))

def watchlist(request):

    #to check if any listings in watchlist are active or not
    active_listings = []
    closed_listings = []
    #check whether this user's watchlist has any listing or not
    try:
        watchlists = Watchlist.objects.filter(user=request.user)
    except Watchlist.DoesNotExist:
        watchlists = None

    #loop over listings in watchlists if watchlists is not None
    listings = [a for a in watchlists if watchlists]
    for listing in listings:
        try:
            active_listing = AuctionListings.objects.get(slug=listing.slug)
            active_listings.append(active_listing)
        except AuctionListings.DoesNotExist:
            closed_listing = ClosedListing.objects.get(slug=listing.slug)
            closed_listings.append(closed_listing)


    if watchlists:
        
            return render(request,'auctions/watchlist.html',{
            'watchlists': watchlists,
            'closed_listings':closed_listings,
            'active_listings': active_listings   
        })
    else:
        return render(request,'auctions/watchlist.html',{
            'watchlists': watchlists,
    
        })

@login_required
def manage_watchlist(request,slug):
    try:
        listing = AuctionListings.objects.get(slug=slug)
    except AuctionListings.DoesNotExist:
        listing = ClosedListing.objects.get(slug=slug)
    #check if listing in the user's watchlist already present or not
    try:
        watchlist = Watchlist.objects.get(user=request.user,slug=listing.slug)
    except Watchlist.DoesNotExist:
        watchlist = None

    #if listing is present in the watchlist
    if watchlist:
        watchlist.delete()

    #if listing is not present in the watchlist
    else:
        watchlist = Watchlist.objects.create(user=request.user,title=listing.title,slug=listing.slug,category=listing.category,
                            starting_bid=listing.starting_bid,image=listing.image)
      
        return redirect(reverse('watchlist'))

    return redirect(reverse('watchlist'))
   

def closed_listing(request):

    closed_listings = ClosedListing.objects.all()

    return render(request,'auctions/closed_listing.html',{
        'closed_listings': closed_listings
    })

def close_auction(request,slug):

    listing = AuctionListings.objects.get(slug=slug)
    closed_listing = ClosedListing.objects.create(title=listing.title,slug=listing.slug,
                        highest_bid=listing.highest_bid,image=listing.image,lister=listing.lister)
    listing.delete()
    highest_bidder = Highest_bidder.objects.last()

    return redirect(reverse('closed_listing_detail',args=(closed_listing.slug,)))

@login_required
def closed_listing_detail(request,slug):

    closed_listing = ClosedListing.objects.get(slug=slug)
    try:
        bidder = Bid.objects.filter(user=request.user)      
    except Bid.DoesNotExist:
        bidder = None

    highest_bidder = Highest_bidder.objects.get(listing_code=closed_listing.slug)
    #check if the user is the one who created the listing
    if request.user == closed_listing.lister:  
        message = 'You have successfully closed the auction'

    #check if the user is the highest bidder
    elif request.user == highest_bidder.user:
        message = 'Congratulations! You have won the auction!'

    #check if the user is one of the bidders
  
    elif bidder:
        message = 'Sorry. You have failed the auction. Good luck next time'
    
    else:
        message = 'This auction has been closed'
        return render(request,'auctions/closed_listing_detail.html',{
        'closed_listing':closed_listing,
        'winner':highest_bidder,
        'message': message
    })
    

    return render(request,'auctions/closed_listing_detail.html',{
        'closed_listing':closed_listing,
        'winner':highest_bidder,
        'message':message
    })

def comment(request,slug):

    listing = AuctionListings.objects.get(slug=slug)    
    highest_bidder = Highest_bidder.objects.get(listing_code=listing.slug)
    if request.method == 'POST':
        cmt = request.POST.get('cmt')     
        Comment.objects.create(session_id=listing.id,user=request.user,comment=cmt)
        #to get the comments made on this listing
        comments = Comment.objects.filter(session_id=listing.id)

        #to check if there are any items in the user's watchlist
        try:
            watchlist = Watchlist.objects.get(user=request.user,slug=listing.slug)
        except Watchlist.DoesNotExist or User.DoesNotExist:
            watchlist = None
            
        #check if the user is the one who created the listing
        if request.user == listing.lister:
            #to give permission to close the auction
            #I assign a variable to the boolean value
            check = True 

            return render(request,'auctions/listing_detail.html',{
                'watchlist': watchlist,
                'listing': listing,
                'highest_bidder': highest_bidder,
                'check': check,
                'comments': comments
            })

        elif request.user == highest_bidder.user:

            return render(request,'auctions/listing_detail.html',{
                'watchlist': watchlist,
                'listing': listing,
                'comments': comments,
                'highest_bidder': highest_bidder
            })

        else:

            return render(request,'auctions/listing_detail.html',{
                'watchlist': watchlist,
                'listing': listing,
                'comments': comments
            })

    else:
        pass
 
        
    return redirect(reverse('listing_detail',args=(listing.slug,)))

    

    

    
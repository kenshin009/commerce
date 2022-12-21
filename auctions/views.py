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

    if request.method == 'POST':
        
        title = request.POST['title']
        slug = slugify(title)
        cat_obj = Category.objects.get_or_create(title=request.POST['category']) 
        description = request.POST['description']
        starting_bid = request.POST['starting_bid']
        image = request.FILES.get('image')
        lister = User.objects.get(id=user_id)
        listing = AuctionListings.objects.create(title=title,slug=slug,category=cat_obj[0],description=description,
                        starting_bid=starting_bid,highest_bid=starting_bid,image=image,lister=lister)
        highest_bidder = Highest_bidder.objects.create(user=lister,listing_code=listing.slug)
        return redirect('index')

    return render(request,'auctions/create_listing.html')

def listing_detail(request,slug):


    listing = AuctionListings.objects.get(slug=slug) 
    #I called the user's own session
    watchlist_id = request.session.get('watchlist_id',None)
    comments = Comment.objects.filter(session_id=listing.id)

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
                'comments': comments
            })
        
        return render(request,'auctions/listing_detail.html',{
            'highest_bidder': highest_bidder,
            'bid': bid,
            'listing': listing,
            'comments': comments
        })
        
    return redirect(reverse('listing_detail',args=(listing.slug,)))

def watchlist(request):

    watchlist_id = request.session.get('watchlist_id',None)
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


    if watchlist_id:
        
            return render(request,'auctions/watchlist.html',{
            'watchlists': watchlists,
            'watchlist_id': watchlist_id,
            'closed_listings':closed_listings,
            'active_listings': active_listings   
        })
    else:
        return render(request,'auctions/watchlist.html',{
            'watchlists': watchlists,
    
        })
    # print(active_listings)
    # return render(request,'auctions/watchlist.html',{
    #     'watchlists': watchlists,
    #     'watchlist_id': watchlist_id,
    #     'closed_listings':closed_listings,
    #     'active_listings': active_listings  
    # })

@login_required
def manage_watchlist(request,slug):

   
    listing = AuctionListings.objects.get(slug=slug)
    highest_bidder = Highest_bidder.objects.get(listing_code=listing.slug)
    #check if listing in watchlist already present or not
    try:
        watchlist = Watchlist.objects.get(title=listing.title)
    except Watchlist.DoesNotExist:
        watchlist = None

    #if listing is not present in the watchlist
    if watchlist is None:
    
        watchlist = Watchlist.objects.create(user=request.user,title=listing.title,slug=listing.slug,category=listing.category,
                            starting_bid=listing.starting_bid,image=listing.image)
        request.session['watchlist_id'] = watchlist.id

    #if listing is already present in the watchlist
    else:
       
        watchlist.delete()
        del request.session['watchlist_id']

        return redirect(reverse('listing_detail',args=(listing.slug,)))

    return redirect(reverse('listing_detail',args=(listing.slug,)))
   

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

def closed_listing_detail(request,slug):

    closed_listing = ClosedListing.objects.get(slug=slug)
    try:
        bidder = Bid.objects.get(id=request.user.id)
        user = User.objects.get(id=request.user.id)
    except Bid.DoesNotExist or User.DoesNotExist:
        bidder = None
        user = None

    highest_bidder = Highest_bidder.objects.get(listing_code=closed_listing.slug)
    #check if the user is the one who created the listing
    if request.user == closed_listing.lister:  
        message = 'The auction has been closed'

    #check if the user is the highest bidder
    elif request.user == highest_bidder.user:
        message = 'Congratulations! You have won the auction!'

    #check if the user is one of the bidders
    elif bidder is not None:
        if request.user == bidder.user:
            message = 'Sorry. You have failed the auction. Good luck next time'
    
    #check if the user is one of the authenticatd users
    elif user is not None:
        if request.user == user:
            message = 'The auction has been closed'

    #if the user is anonymous user
    else:
        return render(request,'auctions/closed_listing_detail.html',{
            'closed_listing': closed_listing
        })

    return render(request,'auctions/closed_listing_detail.html',{
        'closed_listing':closed_listing,
        'winner':highest_bidder,
        'message':message
    })

def comment(request,slug):

    listing = AuctionListings.objects.get(slug=slug)    

    if request.method == 'POST':
        cmt = request.POST.get('cmt')     
        Comment.objects.create(session_id=listing.id,user=request.user,comment=cmt)
        comments = Comment.objects.filter(session_id=listing.id)
        watchlist_id = request.session.get('watchlist_id',None)

        #then I access the user's specific watchlist items
        #to check if there are any items in the watchlist
        try:
            watchlist = Watchlist.objects.filter(id=watchlist_id)
            user = User.objects.get(id=request.user.id)
        except Watchlist.DoesNotExist or User.DoesNotExist:
            watchlist = None
            user = None
            
        #check if the user is the one who created the listing
        if request.user == listing.lister:
            highest_bidder = Highest_bidder.objects.last()
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

        elif user is None:
            return render(request,'auctions/listing_detail.html',{
                'watchlist': watchlist,
                'listing': listing
            })

        else:
            highest_bidder = Highest_bidder.objects.last()
            return render(request,'auctions/listing_detail.html',{
                'watchlist': watchlist,
                'listing': listing,
                'comments': comments,
                'highest_bidder': highest_bidder
            })

    else:
        pass
 
        
    return redirect(reverse('listing_detail',args=(listing.slug,)))

    

    

    
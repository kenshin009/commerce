from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):

    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class AuctionListings(models.Model):

    title = models.CharField(max_length=100)
    slug = models.SlugField(default='')
    category = models.ForeignKey(Category,on_delete=models.CASCADE,default=None)
    description = models.TextField()
    starting_bid = models.PositiveIntegerField()
    highest_bid = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='items')
    created_at = models.DateTimeField(auto_now_add=True)
    lister = models.ForeignKey(User,on_delete=models.CASCADE,default=None)

    def __str__(self):
        return self.title


class Bid(models.Model):

    bid_price = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User,on_delete=models.CASCADE,default='')
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.user.username

class Comment(models.Model):

    session_id = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User,on_delete=models.CASCADE,default='')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class Highest_bidder(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,default='')
    listing_code = models.SlugField(default='')

class Watchlist(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,default='')
    title = models.CharField(max_length=100,default='')
    slug = models.SlugField(default='')
    category = models.ForeignKey(Category,on_delete=models.CASCADE,default=None)
    starting_bid = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='items',blank=True,null=True)

class ClosedListing(models.Model):

    title = models.CharField(max_length=100)
    slug = models.SlugField(default='')
    highest_bid = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='items')
    closed_at = models.DateTimeField(auto_now_add=True)
    lister = models.ForeignKey(User,on_delete=models.CASCADE,default=None)
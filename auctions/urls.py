from django.urls import path

from . import views

urlpatterns = [
    path('comment/<slug:slug>/',views.comment,name='comment'),
    path('closed-listing-detail/<slug:slug>/',views.closed_listing_detail,name='closed_listing_detail'),
    path('closed-listing/',views.closed_listing,name='closed_listing'),
    path('close-auction/<slug:slug>/',views.close_auction,name='close_auction'),
    path('manage-watchlist/<slug:slug>/',views.manage_watchlist,name='manage_watchlist'),
    path('watchlist/',views.watchlist,name='watchlist'),
    path('place-bid/<int:pk>/',views.place_bid,name='place_bid'),
    path('category-detail/<int:pk>/',views.category_detail,name='category_detail'),
    path('categories/',views.categories,name='categories'),
    path('listing-detail/<slug:slug>/',views.listing_detail,name='listing_detail'),
    path('create-listing/<int:user_id>/',views.create_listing,name='create_listing'),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]

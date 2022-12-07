from django.urls import path

from . import views

urlpatterns = [
    path('place-bid/<int:pk>/',views.place_bid,name='place_bid'),
    path('category-detail/<int:pk>/',views.category_detail,name='category_detail'),
    path('categories/',views.categories,name='categories'),
    path('listing-detail/<int:pk>/',views.listing_detail,name='listing_detail'),
    path('create-listing/<int:user_id>/',views.create_listing,name='create_listing'),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]

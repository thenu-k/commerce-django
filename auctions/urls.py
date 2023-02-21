from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('new', views.newListingPage, name='newListing'),
    path('createListing', views.createListing, name='createListing'),
    path('getAllListings', views.getAllListings, name='getAllListings')
]

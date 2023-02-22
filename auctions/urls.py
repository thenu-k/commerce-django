from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('new', views.newListingPage, name='newListing'),
    path('createListing', views.createListing, name='createListing'),
    path('getAllListings', views.getAllListings, name='getAllListings'),
    path('getUserListings', views.getUserListings, name='getUserListings'),
    path('account/<userID>', views.renderAccountPage, name='renderAccountPage')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from account import views as AccountViews
from . import views


urlpatterns = [
    path("", AccountViews.CustomerDashboard, name = "customer"),
    path("profile/", views.cprofile, name = "cprofile")
]
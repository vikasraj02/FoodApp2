from django.urls import path, include
from . import views
from account import views as AccountViews

urlpatterns = [
    path("", AccountViews.VendorDashboard, name = "vendor"),
    path('profile/', views.vprofile, name = 'vprofile'),
]
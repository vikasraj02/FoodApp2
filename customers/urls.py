from django.urls import path, include
from account import views as AccountViews
from . import views

urlpatterns = [
   path('', AccountViews.CustomerDashboard, name = 'customer'),
   path('profile/' , views.cprofile, name = 'cprofile')
]
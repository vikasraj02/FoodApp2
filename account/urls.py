from django.urls import path, include
from . import views


urlpatterns = [
    path("registerUser/",views.registerUser, name="registerUser"),
    path("registerVendor/",views.registerVendor, name="registerVendor"),
    path("login/",views.login, name="login"),
    path("logout/",views.logout, name="logout"),
    path("CustomerDashboard/",views.CustomerDashboard, name="CustomerDashboard"),
    path("VendorDashboard/",views.VendorDashboard, name="VendorDashboard"),
    path("myAccount/", views.myAccount, name="myAccount"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("forgot_password/",views.forgot_password, name = 'forgot_password'),
    path("reset_password_validation/<uidb64>/<token>/",views.reset_password_validation, name = 'reset_password_validation'),
    path("reset_password/",views.reset_password, name = 'reset_password'),
]

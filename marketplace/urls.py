from django.urls import path

from marketplace import views


urlpatterns = [
    path("", views.marketplace, name="marketplace"),
    
    path("<slug:vendor_slug>/", views.vendor_details, name="vendor_details"),
    
    #add to cart
    path("add_to_cart/<int:food_id>/", views.add_to_cart, name='add_to_cart'),
    #decrease cart
    path("decrease_cart/<int:food_id>/", views.decrease_cart, name='decrease_cart'),
    #delete cart
    path("delete_cart/<int:cart_id>/", views.delete_cart, name='delete_cart'),
    
]
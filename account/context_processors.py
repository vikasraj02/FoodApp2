from account.models import UserProfile
from vendor.models import vendor
from django.conf import settings

def get_vendor(request):
    try:
        Vendor = vendor.objects.get(user=request.user)
    except:
        Vendor = None
    return dict(vendor= Vendor)

def get_customer_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None
    return dict(user_profile= user_profile)

def get_google_api(request):
    return {"GOOGLE_API_KEY" : settings.GOOGLE_API_KEY}
    
def get_paypal_client_id(request):
    return {"PAYPAL_CLIENT_ID" : settings.PAYPAL_CLIENT_ID}
    
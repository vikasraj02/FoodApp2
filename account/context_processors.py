from vendor.models import vendor
from django.conf import settings

def get_vendor(request):
    try:
        Vendor = vendor.objects.get(user=request.user)
    except:
        Vendor = None
    return dict(vendor= Vendor)

def get_google_api(request):
    return {"GOOGLE_API_KEY" : settings.GOOGLE_API_KEY}
    
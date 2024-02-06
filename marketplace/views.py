from datetime import date, datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from account.models import UserProfile
from marketplace.models import Cart
from orders.forms import OrderForm
from vendor.models import vendor,OpeningHours
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from .context_processors import get_cart_counter, get_cart_amounts
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

# Create your views here.
def marketplace(request):
    vendors = vendor.objects.filter(is_approved = True , user__is_active = True)
    vendor_count = vendors.count()
    context = {
        "vendors":vendors,
        "vendor_count":vendor_count
    }
    return render(request,'marketplace/listings.html', context)

def vendor_details(request, vendor_slug):
    Vendor = get_object_or_404(vendor, vendor_slug = vendor_slug)
    categories = Category.objects.filter(vendor = Vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset= FoodItem.objects.filter(is_available = True)
            )
    )
    opening_hour = OpeningHours.objects.filter(vendor=Vendor).order_by('day','-from_hour')
    today_date = date.today()
    today = today_date.isoweekday()
    current_opening_hour = OpeningHours.objects.filter(vendor=Vendor, day = today)
    

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None        
    context = {
        "vendor":Vendor,
        "categories":categories,
        "cart_items":cart_items,
        "opening_hour":opening_hour,
        "current_opening_hour":current_opening_hour,

    }
    return render(request,'marketplace/vendor_detail.html',context)


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #check if fooditem exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                #check if user has alredy added that food to the cart
                try:
                    
                    chkCart = Cart.objects.get(user=request.user, fooditem = fooditem)
                    #increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status':'success','message':'Item added to cart successfully and incressed',"cart_counter":get_cart_counter(request), "qty":chkCart.quantity,"cart_amount":get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity = 1)
                    return JsonResponse({"status":"success","message":"Item added to cart successfully","cart_counter":get_cart_counter(request),"qty":chkCart.quantity,"cart_amount":get_cart_amounts(request)})
            except:
                return JsonResponse({"status":"Falied","message":"This food does not exist"})
        else:
            return JsonResponse({"status":"Falied","message":"Invalid request!"})
    else:
        return JsonResponse({"status":"login_required", "message":"Please login"})
    
def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #check if fooditem exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                #check if user has alredy added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem = fooditem)
                    #decrease the cart quantity
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete() 
                        chkCart.quantity = 0
                    return JsonResponse({'status':'success','message':'Item decreased successfully',"cart_counter":get_cart_counter(request), "qty":chkCart.quantity,"cart_amount":get_cart_amounts(request)})
                except:
                    return JsonResponse({"status":"Falied","message":"You dont have this fooditem in your cart"})
            except:
                return JsonResponse({"status":"Falied","message":"This food does not exist"})
        else:
            return JsonResponse({"status":"Falied","message":"Invalid request!"})
    else:
        return JsonResponse({"status":"login_required", "message":"Please login"})

@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    context = {'cart_items':cart_items}
    return render(request, "marketplace/cart.html",context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                #check if the cart item exists in the cart
                cart_item = Cart.objects.get(user=request.user, id = cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'success','message':'cart item has been deleted successfully',"cart_counter":get_cart_counter(request),"cart_amount":get_cart_amounts(request)})
            except:
                return JsonResponse({"status":"Falied","message":"cart item doesnt exist"})
        else:
            return JsonResponse({"status":"Falied","message":"Invalid request!"})
        
def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET.get('address')
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')
        radius = request.GET.get('radius')
        keyword = request.GET.get('keyword')
        #get fooditems the user id looking for
        get_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available = True).values_list("vendor", flat=True)
        vendors = vendor.objects.filter(Q(id__in=get_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        
        
        vendor_count = vendors.count()
        
        if longitude and latitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
            vendors = vendor.objects.filter(Q(id__in=get_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
                user_profile__location__distance_lte=(pnt, D(km=radius))
                ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
            
            for v in vendors:
                v.kms = round(v.distance.km,1)
        
        
        context = {
            "vendors":vendors,
            "vendor_count":vendor_count,
            "source_location": address
        }
        return render(request,'marketplace/listings.html', context)

@login_required(login_url='login') 
def checkout(request):
    cart_items = Cart.objects.filter(user = request.user).order_by("created_at")
    form = OrderForm()
    if cart_items.count() <= 0:
        return redirect("marketplace")
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        "first_name": request.user.first_name,
        "last_name" : request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state':user_profile.state,
        'city': user_profile.city,
        'pin_code':user_profile.pin_code,
        
    }
    form = OrderForm(initial=default_values)
    context = {
        "form":form,
        "cart_items":cart_items
    }
    return render(request,'marketplace/checkout.html', context) 
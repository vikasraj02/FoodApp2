from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart, Tax
from menu.models import FoodItem
from orders.forms import OrderForm
from orders.models import Order, OrderedFood, Payment
import simplejson as json
from .utils import generate_order_number
from account.utils import send_notifaction
from django.contrib.auth.decorators import login_required
import razorpay
from foodonline_main.settings import RZP_KEY_ID, RZP_KEY_SECRET


client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

@login_required(login_url = "login")
def place_order(request):
    cart_items = Cart.objects.filter(user = request.user).order_by("created_at")
    if cart_items.count() <= 0:
        return redirect("marketplace")
    
    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)
            
            
    get_tax = Tax.objects.filter(is_active=True)      
    subtotal = 0
    k = {}
    total_data = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk = i.fooditem.id, vendor_id__in= vendors_ids) 
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            k[v_id] = subtotal
        
        #calucate tax
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100,2)
            tax_dict.update({tax_type:{str(tax_percentage):str(tax_amount)}})
        # construct total data
        total_data.update({fooditem.vendor.id:{str(subtotal):str(tax_dict)}})


    subtotal = get_cart_amounts(request)["subtotal"]
    total_tax = get_cart_amounts(request)["tax"]
    grand_total = get_cart_amounts(request)["grand_total"]
    tax_data = get_cart_amounts(request)["tax_dict"]
    
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save() # order id/ pk is generated
            order.order_number = generate_order_number(order.id)
            order.vedors.add(*vendors_ids)
            order.save()
            
            DATA = {
                    "amount": float(order.total) * 100,
                    "currency": "INR",
                    "receipt": "receipt#"+order.order_number,
                    "notes": {
                        "key1": "value3",
                        "key2": "value2"
                    }
                }
            rzp_order = client.order.create(data=DATA)
            rzp_order_id = rzp_order["id"]
            context = {
                'order': order,
                'cart_items':cart_items,
                "rzp_order_id":rzp_order_id,
                "RZP_KEY_ID": RZP_KEY_ID,
                "rzp_amount": float(order.total) * 100,
            }
            return render(request, "orders/place_order.html",context)

            
        else:
            print(form.errors)
    #print(f"subtotal: {subtotal} total_tax: {total_tax} grand total: {grand_total} tax_data: {tax_data}")
    return render(request, "orders/place_order.html")


@login_required(login_url = "login")
def payments(request):
    # check the request is ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # store the payment details in the payment model
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("transaction_id")
        payment_method = request.POST.get("payment_method")      
        status = request.POST.get("status")      
        
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            status = status,
            amount = order.total,
        )
        payment.save()
        #update the order model
        order.payment = payment
        order.is_ordered = True
        order.save()
        
        # move the cart items to order food model
        
        cart_items = Cart.objects.filter(user = request.user)
        for item in cart_items:
            orderd_food = OrderedFood()
            orderd_food.order = order
            orderd_food.payment = payment
            orderd_food.user = request.user
            orderd_food.fooditem = item.fooditem
            orderd_food.quantity = item.quantity
            orderd_food.price = item.fooditem.price
            orderd_food.amount = item.fooditem.price * item.quantity
            orderd_food.save()
        
        #send order confirmation email to the customer
        mail_subject = "Thank you for ordering with us."
        mail_template = "orders/order_confirmation_email.html"
        context = {
            "user":request.user,
            "order":order,
            "to_email":order.email,
            
        }
        send_notifaction(mail_subject, mail_template, context)
        
        #send order recived email to the vendor
        mail_subject = "We have recived your order"
        mail_template = "orders/new_order_received.html"
        to_emails = []
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)
        context = {
            'order':order,
            'to_email': to_emails,
        }
        send_notifaction(mail_subject, mail_template, context)
        
        # clear the cart of payment is done
        #cart_items.delete()
        # return back to ajax is the status is success of failure
        response = {
            "transaction_id":transaction_id,
            "order_number":order_number,
        }
        return JsonResponse(response)
    return HttpResponse("payments View")

def order_complete(request):
    transcations_id = request.GET.get('trans_id')
    order_number = request.GET.get('order_no')
    try:
        order = Order.objects.get(is_ordered = True, order_number = order_number, payment__transaction_id= transcations_id)
        ordered_food = OrderedFood.objects.filter(order = order)
        subtotal = 0
        
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
            
        tax_data = json.loads(order.tax_data)
        context = {
            "order":order,
            "ordered_food":ordered_food,
            "subtotal":subtotal,
            "tax_data" : tax_data,
        }
        return render(request,"orders/order_complete.html",context) 
    except:
        return redirect('home')
    
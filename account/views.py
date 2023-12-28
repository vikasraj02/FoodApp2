from django.shortcuts import render, HttpResponse, redirect
from account.models import User, UserProfile
from .utils import detectUser

from vendor.forms import VendorForm
from .forms import UserForms
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied
    
# Create your views here.
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request,"your are alredy loggedin")
        return redirect('dashboard')
    elif request.method == 'POST':
        form = UserForms(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.role = user.CUSTOMER
            user.set_password(password)
            user.save()
            messages.success(request,"User saved successfully")
            return redirect("registerUser")
            
    else:
        form = UserForms()
    context = {
        "form" : form,
    }
    return render(request, 'account/registerUser.html',context)

def registerVendor(request):
    if request.method == 'POST':
        form = UserForms(request.POST)
        V_form = VendorForm(request.POST, request.FILES) 

        if form.is_valid() and V_form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.role = user.VENDOR
            user.set_password(password)
            print(user)
            user.save()
            vendor = V_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request,"Vendor registration successfully! plese wait for the approval")
            return redirect("registerVendor")
        else:
            print("it entered into else block")
            
    else:
        form = UserForms()
        V_form = VendorForm()
    context = {
        "form":form,
        "V_form":V_form,
    }
    return render(request, 'account/registerVendor.html', context)

def login(request):
    if request.user.is_authenticated:
        messages.warning(request,"your are alredy loggedin")
        return redirect('myAccount')
    elif request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, "Your now logged in")
            return redirect('myAccount')
        else:
            messages.error(request, "invalid credentials")
            return redirect("login")
    return render(request, 'account/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, "your are logged out")
    return redirect("login")

@login_required(login_url="login")
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url="login")
@user_passes_test(check_role_customer)
def CustomerDashboard(request):
    return render(request, 'account/CustomerDashboard.html')


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def VendorDashboard(request):
    return render(request, 'account/VendorDashboard.html')


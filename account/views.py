from django.shortcuts import render, HttpResponse, redirect
from account.models import User, UserProfile

from vendor.forms import VendorForm
from .forms import UserForms
from django.contrib import messages

# Create your views here.
def registerUser(request):
    if request.method == 'POST':
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
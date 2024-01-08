from django.shortcuts import redirect, render, get_object_or_404
from . forms import VendorForm
from account.forms import UserProfileForm

from account.models import UserProfile
from .models import vendor
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from account.views import check_role_vendor
# Create your views here.

# def vprofile(request):
#     profile = get_object_or_404(UserProfile, user=request.user)
#     Vendor = get_object_or_404(vendor, user=request.user)
    
#     if request.method == 'POST':
#         profile_form = UserProfileForm(request.POST, request.FILES, instance= profile)
#         vendor_form = VendorForm(request.POST, request.FILES, instance= Vendor)
#         if profile_form.is_valid() and vendor_form.is_valid():
#             profile_form.save()
#             vendor_form.save()
#             messages.success(request,"Settings Updated")
#             return redirect('vprofile')
#         else:
#             print("Profile Form Errors:", profile_form.errors)
#             print("Vendor Form Errors:", vendor_form.errors)

#     else:
#         profile_form = UserProfileForm(instance= profile)
#         vendor_form = VendorForm(instance= Vendor)
#     context = {
#         "vendor_form":vendor_form,
#         'profile_form':profile_form,
#         'profile':profile,
#         'Vendor': Vendor,
#     }
#     return render(request, 'vendor/vprofile.html',context)



@login_required(login_url="login")# this line will check the user logged or not if user has not logged in and trying to access the page then it will trow error
@user_passes_test(check_role_vendor) # if loggedin user is cutomer and tried to access vendor dashboard then it will give error
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    Vendor = get_object_or_404(vendor, user=request.user)

    # Initialize forms with or without POST data
    profile_form = UserProfileForm(request.POST or None, request.FILES or None, instance=profile)
    vendor_form = VendorForm(request.POST or None, request.FILES or None, instance=Vendor)

    # Check if the form is submitted and is valid
    if request.method == 'POST' and profile_form.is_valid() and vendor_form.is_valid():
        profile_form.save()
        vendor_form.save()
        messages.success(request, "Settings Updated")
        return redirect('vprofile')
    
    return render(request, 'vendor/vprofile.html', {
        'vendor_form': vendor_form,
        'profile_form': profile_form,
        'profile': profile,
        'Vendor': Vendor,
    })
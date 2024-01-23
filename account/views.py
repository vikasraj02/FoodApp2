from django.shortcuts import render, HttpResponse, redirect
from account.models import User, UserProfile
from .utils import detectUser, send_verifaction_email   
from django.contrib.auth.tokens import default_token_generator
from vendor.forms import VendorForm
from .forms import UserForms
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
import logging
from vendor.models import vendor
from django.template.defaultfilters import slugify


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
        return redirect('myAccount')
    elif request.method == 'POST':
        form = UserForms(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.role = user.CUSTOMER
            user.set_password(password)
            user.save()
            
            #send verifiction email
            mail_subject = "please activate your account"
            email_template = "account/emails/account_verification_email.html"
            send_verifaction_email(request,user, mail_subject,email_template)
            messages.success(request,"User saved successfully")
            return redirect("registerUser")
            
    else:
        form = UserForms()
    context = {
        "form" : form,
    }
    return render(request, 'account/registerUser.html',context)

def registerVendor(request):
    if request.user.is_authenticated:
        messages.success(request,"Your are alredy logged in")
        return redirect("myAccount")
    elif request.method == "POST":
        form = UserForms(request.POST)
        V_form = VendorForm(request.POST, request.FILES) 

        if form.is_valid() and V_form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.role = user.VENDOR
            user.set_password(password)
            user.save()
            vendor = V_form.save(commit=False)
            vendor.user = user
            vendor_name = V_form.cleaned_data["vendor_name"]
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            
            #send verifiction email
            mail_subject = "please activate your account"
            email_template = "account/emails/account_verification_email.html"
            send_verifaction_email(request,user, mail_subject,email_template)
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

@login_required(login_url="login") # this line will check the user logged or not if user has not logged in and trying to access the page then it will trow error
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url="login")# this line will check the user logged or not if user has not logged in and trying to access the page then it will trow error
@user_passes_test(check_role_customer) # if loggedin user is vender and tried to access customer dashboard then it will give error
def CustomerDashboard(request):
    return render(request, 'account/CustomerDashboard.html')


@login_required(login_url="login")# this line will check the user logged or not if user has not logged in and trying to access the page then it will trow error
@user_passes_test(check_role_vendor) # if loggedin user is cutomer and tried to access vendor dashboard then it will give error
def VendorDashboard(request):
    return render(request, 'account/VendorDashboard.html')






logger = logging.getLogger(__name__)
def activate(request, uidb64, token):
    #activate the user by setting the is_activate status to True
    try:
        uid =  urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.error(f"Error during user retrieval: {e}")
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is now activated.")
        return redirect("myAccount")
    else:
        messages.error(request,"Invalid activattion link")
        return redirect("myAccount")

def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]   
        
        if User.objects.filter(email = email).exists():
            user =  User.objects.get(email = email)
            
            #send reset password email
            mail_subject = "please activate your account"
            email_template = "account/emails/reset_password_email.html"
            send_verifaction_email(request,user, mail_subject,email_template)
            
            messages.success(request, "link has been send to yiur mail")
            return redirect("login")
        else:
            messages.error(request, "Account does not exist")
            return redirect("forgot_password")
    return render(request, "account/forgot_password.html")


def reset_password_validation(request, uidb64, token):
    try:
        uid =  urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk = uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.error(f"Error during user retrieval: {e}")
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, "please reser your password")
        return redirect("reset_password")
    else:
        messages.error(request, "this link is expried")
        return redirect("myAccount")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request,"password does not match")
            return redirect('reset_password')
    return render(request, "account/reset_password.html")
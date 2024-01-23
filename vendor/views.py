from django.shortcuts import redirect, render, get_object_or_404
from . forms import VendorForm
from account.forms import UserProfileForm

from account.models import UserProfile
from .models import vendor
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from account.views import check_role_vendor
from menu.models import Category, FoodItem
from menu.forms import CategoryForm,FoodItemForm
from django.template.defaultfilters import slugify

# Create your views here.
def get_vendor (request):
    Vendor = vendor.objects.get(user=request.user)
    return Vendor

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


@login_required(login_url="login")# this line will check the user logged or not if user has not logged in and trying to access the page then it will trow error
@user_passes_test(check_role_vendor) # if loggedin user is cutomer and tried to access vendor dashboard then it will give error
def menu_builder(request):
    Vendor = get_vendor(request)
    categories = Category.objects.filter(vendor = Vendor).order_by('created_at')
    context = {
        "categories":categories
    }
    return render(request, 'vendor/menu_builder.html', context)



@login_required(login_url="login")# this line will check the user logged or not if user has not logged in and trying to access the page then it will trow error
@user_passes_test(check_role_vendor) # if loggedin user is cutomer and tried to access vendor dashboard then it will give error
def fooditems_by_category(request, pk = None):
    Vendor = get_vendor(request)
    category = get_object_or_404(Category, pk = pk)
    fooditems = FoodItem.objects.filter(vendor=Vendor, category=category)
    context = {
        "fooditems":fooditems,
        "category":category,   
    }
    return render(request, 'vendor/fooditems_by_category.html', context)



@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data["category_name"]
            category = form.save(commit=False)
            category.vendor = get_vendor(request)

            # Check if the slug already exists in the database
            slug = slugify(category_name)
            if Category.objects.filter(slug=slug).exists():
                # Handle the case when the slug already exists
                messages.error(request, "Category with this slug already exists.")
                return redirect("menu_builder")

            category.slug = slug
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect("menu_builder")
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    
    context = {'form': form}
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def edit_category(request, pk = None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data["category_name"]
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect("menu_builder")
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form':form,
        "category":category
        }
    return render(request, 'vendor/edit_category.html',context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_category(request, pk = None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect("menu_builder")


# food items #
@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data["food_title"]
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)
            food.save()
            messages.success(request,"Food item saved successfully")      
            return redirect('fooditems_by_category', food.category.id)
    else:      
        form = FoodItemForm()
        form.fields["category"].queryset = Category.objects.filter(vendor = get_vendor(request))
    context = {'form':form,}
    return render(request, 'vendor/add_food.html', context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST,request.FILES, instance=food )
        if form.is_valid():
            foodtile = form.cleaned_data["food_title"]
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtile)
            form.save()
            messages.success(request,"Food item edited successfully")
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food)
        form.fields["category"].queryset = Category.objects.filter(vendor = get_vendor(request))
    context = {
        'form' : form,
        "food":food
    }
    return render(request, 'vendor/edit_food.html', context)

@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request,"Food item deleted successfully")
    return redirect('fooditems_by_category', food.category.id)
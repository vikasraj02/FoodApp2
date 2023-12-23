from django.shortcuts import render, HttpResponse, redirect
from .forms import UserForms
from django.contrib import messages

# Create your views here.
def registerUser(request):
    if request.method == 'POST':
        form = UserForms(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.Role = user.CUSTOMER
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
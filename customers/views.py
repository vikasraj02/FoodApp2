from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from account.forms import UserInfo, UserProfileForm
from account.models import UserProfile
from django.contrib import messages

@login_required(login_url='login')
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfo(request.POST,instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'profile updated')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfo(instance=request.user)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile':profile
    }
    return render(request, 'customers/cprofile.html',context)
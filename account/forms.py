from django import forms
from .models import User, UserProfile
from . validators import allow_only_Images_validator


class UserForms(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_Password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['first_name','last_name','email','password','username','confirm_Password']
        
    def clean(self):
        # Check if both passwords are the same
        cleaned_data = super(UserForms, self).clean()
        password = cleaned_data.get('password')
        confirm_Password = cleaned_data.get("confirm_Password")
        
        if password != confirm_Password:
            raise forms.ValidationError(
                "password not matched"
            )
class UserProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Start typing...', 'required': 'required'}))
    profile_picture = forms.ImageField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}))
    cover_photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}))
    
    
    latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture','cover_photo','address','country','state','city','pin_code','latitude','longitude']
        
    # def __ini__(self, *args, **kwargs):
    #     super(UserProfileForm, self).__init__(*args,**kwargs)
    #     for field in self.fields:
    #         if field == 'latitude' or field == 'longitude':
    #             self.fields[field].widget.attrs['readonly'] = 'readonly'
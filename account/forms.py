from django import forms
from .models import User

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
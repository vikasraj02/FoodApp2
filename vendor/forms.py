from django import forms
from .models import OpeningHours
from account.validators import allow_only_Images_validator 

from . models import vendor

class VendorForm(forms.ModelForm):
    vendor_license = forms.ImageField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}))
    class Meta:
        model = vendor
        fields = ['vendor_name', 'vendor_license']
        
#VendorForm.base_fields['vendor_license'].required = False

class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = OpeningHours
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']
        
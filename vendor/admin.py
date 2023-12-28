from django.contrib import admin

from vendor.models import vendor

class vendor_admin (admin.ModelAdmin):
    list_display = ("user","vendor_name","is_approved","created_at")
    list_display_link = ("user","vendor_name")

# Register your models here.
admin.site.register(vendor,vendor_admin)
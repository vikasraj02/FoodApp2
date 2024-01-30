from django.contrib import admin

from vendor.models import OpeningHours, vendor

class vendor_admin (admin.ModelAdmin):
    list_display = ("user","vendor_name","is_approved","created_at")
    list_display_link = ("user","vendor_name")

class OpeningHourAmin(admin.ModelAdmin):
    list_display = ('vendor', 'day','from_hour','to_hour')

# Register your models here.
admin.site.register(vendor,vendor_admin)
admin.site.register(OpeningHours,OpeningHourAmin)
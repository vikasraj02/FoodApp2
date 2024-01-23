from django.db import models
from account.models import User, UserProfile
from account.utils import send_notifaction

# Create your models here.
class vendor(models.Model):
   user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
   user_profile =  models.OneToOneField(UserProfile, related_name="userprofile", on_delete=models.CASCADE)
   vendor_name = models.CharField(max_length=50)
   vendor_slug = models.SlugField(max_length=100, unique=True)
   vendor_license = models.ImageField(upload_to="vendor/license")
   is_approved = models.BooleanField(default=False)
   created_at = models.DateTimeField(auto_now_add=True)
   modified_at = models.DateTimeField(auto_now=True)
   
   def __str__(self):
       return self.vendor_name
   
   def save(self, *args, **kwargs):
       if self.pk is not None:
           orgin = vendor.objects.get(pk=self.pk)
           if orgin.is_approved != self.is_approved:
               mail_template = "account/emails/admin_approval_email.html"
               context = {
                   "user" :self.user,
                   "is_approved" : self.is_approved
               }
               if self.is_approved == True:
                   #send notifaction email
                   mail_subject = "congratulation your restaurant has been approved."
                   send_notifaction(mail_subject,mail_template,context)
               else:
                   #send notifaction email
                   mail_subject = "sorry we anre not eligible for publishing food menu on our market."
                   send_notifaction(mail_subject,mail_template,context)
       return super(vendor, self).save(*args, **kwargs)



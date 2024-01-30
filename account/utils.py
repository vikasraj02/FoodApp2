from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings
from foodonline_main.settings import EMAIL_HOST,EMAIL_PORT,EMAIL_HOST_USER,EMAIL_HOST_PASSWORD


def detectUser(user):
    if user.role == 1:
        redirectUrl = 'VendorDashboard'
        return redirectUrl
    elif user.role == 2:
        redirectUrl = 'CustomerDashboard'
        return redirectUrl
    elif user.role == None and user.is_superadmin:
         redirectUrl = '/admin'
         return redirectUrl
     
def send_verifaction_email(request, user, mail_subject,email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    
    message =  render_to_string(email_template,{
        "user": user,
        "domain": current_site,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user)
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message,from_email, to=[to_email])
    mail.send()
    
def send_notifaction(mail_subject,mail_template,context):
     print("EMAIL_HOST:", EMAIL_HOST)
     print("EMAIL_PORT:", EMAIL_PORT)
     print("EMAIL_HOST_USER:", EMAIL_HOST_USER)
     print("EMAIL_HOST_PASSWORD:", EMAIL_HOST_PASSWORD)
     from_email = settings.DEFAULT_FROM_EMAIL
     message = render_to_string(mail_template, context)
     to_email = context["user"].email
     mail = EmailMessage(mail_subject, message,from_email, to=[to_email],)
     mail.send()
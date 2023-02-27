from django.shortcuts import redirect, render
from django.http import HttpResponse 
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from ecommerce_web_application import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import *
import re

# Create your views here.
def home(request):
    #return HttpResponse("Home Page")
    return render(request, 'index.html', {})
    
def signup(request):
    
    if request.method == "POST":
        username = request.POST.get("username")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        password = request.POST.get("password1")
        confirmPassword = request.POST.get("password2")

        # Check if user already exists
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists! try othe username")
            return redirect("home")
        
        if User.objects.filter(email=email):
            messages.error(request, "email already registered!")
            
        if len(username)>10:
            messages.error(request, "Username must be under 10 characters")
            
        if password != confirmPassword:
            messages.error(request, "Password didn't match!")
            
        if not username.isalnum():
            messages.error(request, "Username must be alpha-numeric")
            return redirect("home")
            
        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = firstname
        myuser.last_name = lastname
        # Make user inactive untile get verified via link send via email
        myuser.is_active = False

        # Save user
        myuser.save()
        messages.success(request, "Account created successfully! Please check your email account for activation link!")
        
        # Welcome email to user
        subject = "Welcome to Django Authentication"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Django Authentication! \n Thank you for visiting our website \n please confirm your email address in order to activate your account. \n Thank You"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        # Check Confirmation email
        current_site = get_current_site(request)
        email_subject = "Confirm your email @ Django Authentication login"
        message2 = render_to_string('authentication/email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        
        email.fail_silently = True
        email.send()
        
        return redirect("signin")
    
    return render(request, 'authentication/signup.html', {})

def signin(request):
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password1")
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("user_home")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("home")
    
    return render(request, 'authentication/signin.html', {})

def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("home")
    
def user_home(request):
    return render(request, "authentication/home.html", {})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
        
    # Activate user
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect("user_home")
    else:
        return render(request, 'authentication/activation_failed.html')
    
def forget_password(request):
    
    if request.method == 'POST':
        username = request.POST.get("username")
        
        if not User.objects.filter(username=username).first():
            messages.error(request, "No user found with this usename")
            return redirect("forget_password")
        else:
            myuser = User.objects.get(username=username)
            domain = get_current_site(request).domain
            token = generate_token.make_token(myuser)
            uidb4 = urlsafe_base64_encode(force_bytes(myuser.pk))
            
            subject = "Djangi Authentication - forget password link"
            message = f"Hi , Click on the link to reset your password http://{ domain }/auth/reset-password/{uidb4}/{token}"
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            messages.success(request, "reset password link send on "+ myuser.email +" successfully")
    
    return render(request, 'authentication/forget_password.html', {})

def reset_password(request, uidb64, token):
    
    if request.method == "POST":
        password = request.POST.get("password1")
        confirmPassword = request.POST.get("password2")
        user_id = force_str(urlsafe_base64_decode(uidb64))
        
        try:
            myuser = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            myuser = None
        
        if password != confirmPassword:
            messages.error(request, "Password didn't match!")
        
        if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            #messages.error(request, "valid="+password)
            if myuser is not None and generate_token.check_token(myuser, token):
                myuser.set_password(password)
                myuser.save()
                return redirect("signin")
            else:
                messages.error(request, "No user found")
        else:
            messages.error(request, "Password must be alpha-numeric")
           
    return render(request, 'authentication/reset_password.html')


from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.utils import timezone

from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, get_user_model, authenticate
from django.contrib import messages

from .methods import *

import hashlib

from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import PasswordResetToken
import secrets
import hashlib

from datetime import timedelta

 
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse
 

from .models import PasswordResetToken


User = get_user_model()
# Create your views here.

def displayHomePage(request):
    matches = Match.objects.all().count()
    results = Result.objects.all().count()
    products = Product.objects.all()
    
    now = timezone.now()
    next_match = Match.objects.filter(datetime_played__gte=now).order_by('datetime_played').first()
    last_results = Result.objects.filter(datetime_played__lte=now).order_by('-datetime_played')[:3]
    if News.objects.all():
        news = News.objects.filter(date_edited__lte=now).order_by('-date_edited')[:3]#len(News.objects.filter(date_edited__lte=now).order_by('date_edited')) - 3]
    else:
        news = False
        
    return render(request, "home/home.html", {"matches": matches, "results": last_results, "products": products, "next_match": next_match, "news": news})
    
def displayMatchesPage(request):
    now = timezone.now()
    matches = Match.objects.filter(datetime_played__gte=now).order_by('datetime_played')[1:]
    next_match = Match.objects.filter(datetime_played__gte=now).order_by('datetime_played').first()
    results = Result.objects.filter(datetime_played__lte=now).order_by('-datetime_played')
    return render(request, "home/matches.html", {"fixtures": matches, "results": results, "next_fixture": next_match})
    
def displayTeamPage(request):
    return render(request, "home/team.html")
    
def displayShopPage(request):
    products = Product.objects.all()
    
    return render(request, "home/shop.html", {"products": products})
    
def displayNewsPage(request):
    news = News.objects.all().order_by('-date_edited')
    
    return render(request, "home/news.html", {"news": news})
    
def displayAboutPage(request):
    return render(request, "home/about.html")
    
def displayContactPage(request):
    return render(request, "home/contact.html")

def displayPaymentPage(request, productID):
    product = get_object_or_404(Product, id=int(productID))
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')

        if not is_valid_kenyan_phone(phone_number):
            return render(request, "home/pay.html", {'form': product, "errorMsg": 'Phone Number is Invalid'})

        product_size = request.POST.get('product_size')
        user_email = request.POST.get('user_email')
        print(user_email)
        product_name = product.data_product
        product_price = product.data_price

        cl = MpesaClient()
        account_reference = 'APS Bomet FC'
        transaction_desc = 'Kit Purchase'

        callback_url = 'https://defacing-murmuring-devourer.ngrok-free.dev/mpesa/callback/' 
        try:
            response = cl.stk_push(phone_number, product_price, account_reference, transaction_desc, callback_url)
        
            print("Response:", vars(response))

            file_path = os.path.join(settings.BASE_DIR, "user_products.json")
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

            subject = "APS BOMET FC Payment"
            message = """
            Hello User,
            
            We Have Confirmed your Payment Details!

            Thank you for registering with us.
            
            Regards,
            Admin
            """
            
            recipient = user_email
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient],
                fail_silently=False,
            )    
            return HttpResponse(response)
            
        except Exception as e:
            print("Payment error:", str(e))

        #return HttpResponse(response)

    form = product   
    return render(request, "home/pay.html", {'form': form, 'errorMsg': ''})

def save_json(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        
        file_path = os.path.join(settings.BASE_DIR, "user_products.json")

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

        return JsonResponse({'status': "success", "message": "JSON File Created!"})    

    return JsonResponse({'status': 'error'}, status=400)   

#@require_POST
#@csrf_protect
def initiate_stk_push(request, phone_number, amount):
    client = MpesaClient()
    phone_number = phone_number
    amount = amount
    account_reference = 'APS Bomet FC'
    transaction_desc = "Kit Purchase"

    callback_url = 'https://defacing-murmuring-devourer.ngrok-free.dev/mpesa/callback/'
    response = client.stk_push(
        phone_number,
        amount,
        account_reference,
        transaction_desc,
        callback_url
    )

    return HttpResponse(response)

@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        # Safaricom sends JSON data payload containing transaction details (Receipt number, status, etc.)
        data = json.loads(request.body)
        
        # Parse and save transaction details to your database here
        print(data)
        
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    
    return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid Request Method"})


def not_logged_in(user):
    return not user.is_authenticated


#@user_passes_test(not_logged_in, login_url='homeApp:login')



def signin(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = UserCreationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()

            # Automatically log in the newly registered user
            login(request)

            subject = "APS BOMET FC User Registration"

            message = f"""
Hello {user.username}!

Thank you for registering with us.

Regards,
APS BOMET FC ADMIN,
Derrick Chirchir.
"""

            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False
                )

                messages.success(
                    request,
                    'Account created successfully!'
                )

            except Exception as e:
                print('Email Error:', str(e))

                messages.warning(
                    request,
                    'Account created, but the welcome email could not be sent.'
                )

            return redirect('home')
    #print(form)        
    return render(request, 'home/signin.html', {'form': form})


def login(request):

    if request.user.is_authenticated:
        return redirect('home')

    error = None
    email = ''

    if request.method == 'POST':

        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        User = get_user_model()

        # Find account using email
        users = User.objects.filter(email__iexact=email)

        if users.count() == 1:

            user = users.first()

            # Authenticate using the actual username
            authenticated_user = authenticate(
                request,
                username=user.username,
                password=password
            )

            if authenticated_user is not None:

                login(request, authenticated_user)

                return redirect('home')

        error = 'Invalid email or password.'

    return render(
        request,
        'home/login.html',
        {
            'error': error,
            'email': email
        }
    )
    
def resetpass(request):
    if not request.user.is_authenticated:
        return redirect('signin')
        
    return render(request, 'home/forgot-pass.html')
    

def password_reset_confirm(request, token):

    # Hash the supplied token
    token_hash = hashlib.sha256(
        token.encode()
    ).hexdigest()

    # Retrieve the corresponding record
    reset = PasswordResetToken.objects.filter(
        token_hash=token_hash
    ).select_related('user').first()

    # Check token validity
    if not reset or not reset.is_valid():

        return render(
            request,
            'home/password_reset_invalid.html'
        )

    error = None

    if request.method == 'POST':

        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if password1 != password2:

            error = "Passwords do not match."

        else:

            try:

                # Apply Django's password validation rules
                validate_password(password1, reset.user)

                # Change the user's password securely
                reset.user.set_password(password1)
                reset.user.save()

                # Invalidate the token
                reset.used_at = timezone.now()
                reset.save(update_fields=['used_at'])

                messages.success(
                    request,
                    'Your password has been changed successfully.'
                )

                return redirect('signin')

            except ValidationError as e:

                error = " ".join(e.messages)

    return render(
        request,
        'home/password_reset_confirm.html',
        {
            'error': error,
            'token': token
        }
    )
    
def forgot_password(request):

    message = None

    if request.method == 'POST':

        email = request.POST.get('email', '').strip()

        # Find the account associated with this email
        users = User.objects.filter(
            email__iexact=email,
            is_active=True
        )

        if users.count() == 1:

            user = users.first()

            # Generate a secure random token
            token = secrets.token_urlsafe(32)

            # Hash the token before saving
            token_hash = hashlib.sha256(
                token.encode()
            ).hexdigest()

            # Save token in database
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token_hash=token_hash,
                expires_at=timezone.now() + timedelta(minutes=15)
            )

            # Generate reset URL
            reset_url = request.build_absolute_uri(
                reverse(
                    'password_reset_confirm',
                    kwargs={'token': token}
                )
            )

            subject = "APS BOMET FC - Password Reset"

            email_message = f"""
Hello {user.username},

We received a request to reset your APS BOMET FC account password.

Click the link below to reset your password:

{reset_url}

This link expires in 15 minutes.

If you did not request this, ignore this email.

Regards,
APS BOMET FC ADMIN,
Derrick Chirchir.
"""

            try:

                sent = send_mail(
                    subject,
                    email_message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False
                )
                print(sent)
                if sent != 1:
                    raise Exception("Email was not accepted by the email backend.")

            except Exception as e:

                # Remove unusable token if email sending fails
                reset_token.delete()

                print("Password Reset Email Error:", str(e))

        # Same response whether email exists or not
        message = (
            "If an account exists with that email, "
            "password reset instructions will be sent."
        )

    return render(
        request,
        'home/forgot_pass.html',
        {'message': message}
    )
    
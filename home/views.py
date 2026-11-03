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
from django.views.decorators.csrf import csrf_protect

from .methods import *
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
    """
    if request.method == "POST":
        data = json.loads(request.body)
        cl = MpesaClient()
        phone_number = data.get(phone_number)
        amount = data.get(amount)
        account_reference = 'APS Bomet FC'
        transaction_desc = 'Kit Purchase'

        callback_url = 'https://defacing-murmuring-devourer.ngrok-free.dev/mpesa/callback/' 
        try:
            response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
            
            print("Response:", vars(response)

        except Exception as e:
            print("Payment error:", str(e))

        #return HttpResponse(response)
        
    return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid Request Method"})
    """
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


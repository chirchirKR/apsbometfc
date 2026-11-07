from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name = "homeApp"

urlpatterns = [
    path('', views.displayHomePage, name='home'),
    path('matches/', views.displayMatchesPage, name='matches'),
    path('shop/', views.displayShopPage, name='shop'),
    path('news/', views.displayNewsPage, name='news'),
    path('team/', views.displayTeamPage, name='team'),
    path('about/', views.displayAboutPage, name='about'),
    path('contact/', views.displayContactPage, name='contact'),
    path('pay/', views.initiate_stk_push, name='initiate_stk_push'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('proceedNpay/<str:productID>/', views.displayPaymentPage, name='payment'),
    path('save-json/', views.save_json,  name='save-json'),
    #path('signin/', views.signin, name='signin'),
    #path('login/', views.login, name='login'),
    #path('forgot_password/', views.forgot_password, name='resetpass'),
    #path('reset/<str:token>/', views.password_reset_confirm, name='token')
]
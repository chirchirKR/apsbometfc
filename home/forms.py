from django import forms

class PaymentDetail(forms.Form):
    phone_number = forms.IntegerField()
from django import forms
from .models import Order

class OrderForm(forms.Form):
    customer_name = forms.CharField(max_length=255, label='نام مشتری')
    shipping_address = forms.CharField(widget=forms.Textarea, label='آدرس ارسال')
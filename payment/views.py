from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import Order


def process_payment(request, order_id):  # order_id به عنوان پارامتر دریافت می‌شود
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # در اینجا منطق پرداخت را پیاده‌سازی کنید
    context = {
        'order': order,
        'total_price': order.total_price
    }
    return render(request, 'payment/payment.html', context)


def payment_callback(request):
    # منطق بازگشت از درگاه پرداخت
    return render(request, 'payment/callback.html')


def verify_payment(request, order_id):
    # منطق تایید پرداخت
    return render(request, 'payment/verify.html')
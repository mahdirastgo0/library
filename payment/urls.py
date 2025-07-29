from django.urls import path
from . import views

app_name = 'payment'  # این خط حیاتی است

urlpatterns = [
    path('process/<int:order_id>/', views.process_payment, name='process'),  # تغییر این خط
    path('callback/', views.payment_callback, name='callback'),
]
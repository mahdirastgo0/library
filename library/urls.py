

from django.urls import path , include
from . import views

app_name = 'library'

urlpatterns = [

    path('', views.home, name='home'),
    path("library/", views.library, name="library"),
    path("books/", views.Books, name="books"),
    path("cart/", views.cart, name="cart"),
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('error_page/', views.error_page, name='error_page'),
    path('success_page/', views.success_page, name='success_page'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('process-payment/<int:order_id>/<str:email>/', views.process_payment, name='process_payment'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),


]
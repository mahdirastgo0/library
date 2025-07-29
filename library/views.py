import json
import logging
from datetime import timedelta
from django.http import (HttpResponse, HttpResponseForbidden,
                        JsonResponse, HttpResponseBadRequest)
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction, models
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django_recaptcha.fields import ReCaptchaField
from django_ratelimit.decorators import ratelimit
from rest_framework.throttling import UserRateThrottle

from accounts.models import (Book, Genre, qoute, CartItem, Delivery,
                           Order, OrderItem, User, Author, Cart)

logger = logging.getLogger(__name__)


def home(request):
    best_sellers = Book.objects.filter(status="sold").order_by("-price")[:1]
    featured_books = Book.objects.filter(featured="featured").order_by("-year_published")[:4]
    popular_books = Book.objects.filter(featured="popular").order_by("-year_published")[:4]

    # Get distinct genres, ensuring they are ordered correctly
    genres = Genre.objects.all()

    # Handle genre filtering (case-insensitive)
    selected_genre = request.GET.get("genre", "").strip()
    books = Book.objects.all()
    random_quote = qoute.objects.order_by('?').first()

    return render(
        request,
        "library/home.html",
        {
            "books": books,
            "popular_books": popular_books,
            "selected_genre": selected_genre,
            "genres": genres,
            "featured_books": featured_books,
            "best_sellers": best_sellers,
            'random_quote': random_quote,
        },
    )


def library(request):
    return render(request, 'library/cart.html')


# @login_required
# @require_POST
# def add_to_cart(request, book_id):
#     try:
#         book = get_object_or_404(Book, pk=book_id)
#
#         # دریافت یا ایجاد سبد خرید
#         cart, created = Cart.objects.get_or_create(
#             user=request.user if request.user.is_authenticated else None,
#             session_key=request.session.session_key if not request.user.is_authenticated else None
#         )
#
#         # دریافت یا ایجاد آیتم سبد خرید
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             product=book,
#             defaults={'quantity': 1}
#         )
#
#         if not created:
#             cart_item.quantity += 1
#             cart_item.save()
#
#         # حالا می‌توانید از cart.items استفاده کنید
#         cart_count = cart.items.count()
#
#         return JsonResponse({
#             'success': True,
#             'cart_count': cart_count,
#             'message': 'محصول با موفقیت به سبد خرید اضافه شد'
#         })
#
#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'error': str(e)
#         }, status=400)

@require_POST
def add_to_cart(request, book_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'برای افزودن به سبد خرید ابتدا وارد شوید.'}, status=401)

    try:
        if not request.session.session_key:
            request.session.save()

        book = get_object_or_404(Book, pk=book_id)

        cart, _ = Cart.objects.get_or_create(
            user=request.user,
            session_key=request.session.session_key,
        )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=book,
            defaults={
                'quantity': models.F('quantity') + 1 if not created else 1,
                'owned': False,
            }
        )
        print(f"Cart item created: {created}, Quantity: {cart_item.quantity}")

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({
            'success': True,
            'cart_count': cart.items.count(),
            'message': 'کتاب با موفقیت به سبد خرید اضافه شد'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def product_list(request):
    # Fetch all products
    books = Book.objects.all()
    return render(request, 'library/product_list.html', {'products': books})


# def get_cart_for_request(request):
#     if request.user.is_authenticated:
#         cart = Cart.objects.filter(user=request.user).first()
#         if not cart:
#             cart = Cart.objects.create(user=request.user)
#     else:
#         if not request.session.session_key:
#             request.session.create()
#         session_key = request.session.session_key
#         cart = Cart.objects.filter(session_key=session_key).first()
#         if not cart:
#             cart = Cart.objects.create(session_key=session_key)
#     return cart

def get_cart_for_request(request):
    if request.user.is_authenticated:
        # فقط یک سبد آخر رو می‌گیریم
        cart = Cart.objects.filter(user=request.user).order_by('-created_at').first()
        if not cart:
            cart = Cart.objects.create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        cart = Cart.objects.filter(session_key=session_key).order_by('-created_at').first()
        if not cart:
            cart = Cart.objects.create(session_key=session_key)

    return cart

def cart(request):
    cart = get_cart_for_request(request)
    cart_items = cart.items.all()

    total_price = sum(item.total_price for item in cart_items)
    total_items = cart_items.count()

    # تلاش برای گرفتن روش ارسال انتخاب شده
    delivery_method_id = request.session.get('delivery_method', None)
    delivery_cost = 0
    total_price_with_delivery = total_price

    # مدیریت ارسال فرم در صورت POST
    if request.method == 'POST':
        delivery_method_id = request.POST.get('delivery_method')
        if delivery_method_id:
            try:
                delivery_method = Delivery.objects.get(id=delivery_method_id)
                delivery_cost = delivery_method.price
                total_price_with_delivery = total_price + delivery_cost

                # ذخیره اطلاعات در session
                request.session['delivery_method'] = delivery_method_id
                request.session['delivery_cost'] = float(delivery_cost)
                request.session['total_price_with_delivery'] = float(total_price_with_delivery)

                messages.success(request, "روش تحویل با موفقیت به‌روز شد")
            except Delivery.DoesNotExist:
                messages.error(request, "روش تحویل انتخاب شده معتبر نیست")
        else:
            messages.error(request, "لطفاً یک روش تحویل انتخاب کنید.")

    elif delivery_method_id:
        try:
            delivery_method = Delivery.objects.get(id=delivery_method_id)
            delivery_cost = delivery_method.price
            total_price_with_delivery = total_price + delivery_cost
        except Delivery.DoesNotExist:
            messages.error(request, "روش تحویل انتخابی معتبر نیست.")

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': total_items,
        'Delivery_methods': Delivery.objects.all(),
        'selected_delivery_method': delivery_method_id,
        'delivery_cost': delivery_cost,
        'total_price_with_delivery': total_price_with_delivery,
    }

    return render(request, 'library/cart.html', context)



def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    # اطمینان از اینکه فقط آیتم‌های سبد خرید فعلی حذف می‌شن
    cart = get_cart_for_request(request)
    if cart_item.cart != cart:
        return redirect('library:cart')

    cart_item.delete()
    messages.success(request, "آیتم از سبد خرید حذف شد.")
    return redirect('library:cart')


# @require_POST
# @csrf_exempt
# def update_cart(request):
#     try:
#         data = json.loads(request.body)
#
#         product_id = data.get('product_id')
#         action = data.get('action')
#
#         if not product_id or action not in ['increase', 'decrease']:
#             return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
#
#         # یافتن سبد خرید
#         if request.user.is_authenticated:
#             cart = Cart.objects.get(user=request.user)
#         else:
#             if not request.session.session_key:
#                 request.session.create()
#             cart = Cart.objects.get(session_key=request.session.session_key)
#
#         # یافتن محصول
#         product = Book.objects.get(book_id=product_id)
#
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             product=product,
#             defaults={'quantity': 1}
#         )
#
#         # به‌روزرسانی مقدار
#         if action == 'increase':
#             cart_item.quantity += 1
#         elif action == 'decrease':
#             cart_item.quantity = max(1, cart_item.quantity - 1)
#
#         cart_item.save()
#
#         # محاسبه قیمت کل
#         total_price = sum(item.total_price for item in cart.items.all())
#
#         return JsonResponse({
#             'status': 'success',
#             'new_quantity': cart_item.quantity,
#             'total_price': str(cart_item.total_price),
#             'product_id': product_id,
#             'total_price_all': total_price
#         })
#
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

# @require_POST
# def update_cart(request):
#     try:
#         # دریافت داده‌ها از POST
#         product_id = request.POST.get('product_id')
#         action = request.POST.get('action')
#
#         print(f"Product ID: {product_id}, Action: {action}")
#         # بررسی داده‌های ورودی
#         if not product_id or action not in ['increase', 'decrease']:
#             return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
#
#         # یافتن سبد خرید
#         if request.user.is_authenticated:
#             cart = get_object_or_404(Cart, user=request.user)
#         else:
#             if not request.session.session_key:
#                 request.session.create()
#             cart = get_object_or_404(Cart, session_key=request.session.session_key)
#
#         # یافتن محصول با استفاده از product_id
#         product = get_object_or_404(Book, pk=product_id)
#
#         # یافتن یا ایجاد CartItem
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart,
#             product=product,
#             defaults={'quantity': 1}
#         )
#
#         # به‌روزرسانی مقدار
#         if action == 'increase':
#             cart_item.quantity += 1
#         elif action == 'decrease':
#             cart_item.quantity = max(1, cart_item.quantity - 1)
#
#         cart_item.save()
#
#         # محاسبه قیمت کل
#         total_price = sum(item.total_price for item in cart.items.all())
#
#         return JsonResponse({
#             'status': 'success',
#             'new_quantity': cart_item.quantity,
#             'total_price': str(cart_item.total_price),
#             'product_id': product_id,
#             'total_price_all': total_price,
#         })
#
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


@require_POST
def update_cart(request):
    try:
        # دریافت داده‌ها از POST
        cart_item_id = request.POST.get('cart_item_id')
        action = request.POST.get('action')

        # بررسی داده‌های ورودی
        if not cart_item_id or action not in ['increase', 'decrease']:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

        # یافتن سبد خرید
        if request.user.is_authenticated:
            carts = Cart.objects.filter(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            carts = Cart.objects.filter(session_key=request.session.session_key)

        if not carts.exists():
            return JsonResponse({'status': 'error', 'message': 'Cart not found'}, status=404)

        # اگر چند سبد خرید وجود دارد، فقط اولی را نگه دارید
        if carts.count() > 1:
            # حذف سبدهای اضافی
            main_cart = carts.first()
            carts.exclude(id=main_cart.id).delete()
        else:
            main_cart = carts.first()

        # یافتن CartItem
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=main_cart)

        # به‌روزرسانی مقدار
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            cart_item.quantity = max(1, cart_item.quantity - 1)

        cart_item.save()

        # محاسبه قیمت کل
        total_price = sum(item.total_price for item in main_cart.items.all())

        return JsonResponse({
            'status': 'success',
            'new_quantity': cart_item.quantity,
            'total_price': str(cart_item.total_price),
            'product_id': cart_item.product.book_id,
            'total_price_all': total_price
        })

    except Exception as e:
        # چاپ دقیق‌تر خطا برای کمک به شناسایی مشکل
        print(f"Error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@ratelimit(key='ip', rate='3/m')
@login_required
@require_http_methods(["POST"])
@transaction.atomic
def checkout(request):
    try:
        cart = get_cart_for_request(request)
        if not cart or not cart.items.exists():
            messages.error(request, "سبد خرید شما خالی است")
            return redirect('library:cart')

        # محاسبه جمع کل
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())

        # ایجاد سفارش با مقادیر پیش‌فرض
        order = Order.objects.create(
            user=request.user,
            total_price=total_price or 0.00,  # تضمین مقدار پیش‌فرض
            status='pending'
        )

        # ایجاد آیتم‌های سفارش
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            ) for item in cart.items.all()
        ])

        return redirect('payment:process', order_id=order.id)

    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        messages.error(request, "خطا در پردازش سفارش")
        return redirect('library:cart')


def payment_callback(request):
    try:
        order_id = request.session.get('pending_order')
        if not order_id:
            raise ValueError("سفارش مورد نظر یافت نشد")

        order = Order.objects.get(id=order_id, status='draft')

        if payment_is_successful:  # این شرط را با منطق پرداخت واقعی جایگزین کنید
            with transaction.atomic():
                # بروزرسانی وضعیت سفارش
                order.status = 'completed'
                order.payment_date = timezone.now()
                order.save()

                # علامت‌گذاری آیتم‌های سبد خرید
                CartItem.objects.filter(
                    cart__user=request.user,
                    owned=False
                ).update(owned=True)

                # حذف سفارش از session
                del request.session['pending_order']

                messages.success(request, "پرداخت با موفقیت انجام شد")
                return redirect('library:order_detail', order_id=order.id)
        else:
            order.status = 'failed'
            order.save()
            messages.error(request, "پرداخت ناموفق بود")
            return redirect('library:cart')

    except Exception as e:
        print(f"خطا در پردازش callback: {str(e)}")
        messages.error(request, "خطایی در پردازش پرداخت رخ داد")
        return redirect('library:cart')

def error_page(request):
    return render(request, 'library/error_page.html')


def success_page(request):
    return render(request, 'library/success_page.html')


def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'library/payment.html', context)


def process_payment(request, order_id, email):
    # Get the order using the order_id
    order = get_object_or_404(Order, id=order_id)

    # Get the customer using the email
    Customer = get_object_or_404(User, email=email)

    # If the order is already paid, redirect to the order detail page
    if order.is_paid:
        return redirect('library:order_detail', order_id=order.id)

    # Render the payment page, passing order and customer data
    return render(request, 'library/payment.html', {'order': order, 'Customer': Customer})


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'library/order_detail.html', context)


def Books(request):
    books = Book.objects.all()

    # فیلترها
    author = request.GET.get('author')
    genre = request.GET.get('genre')
    year = request.GET.get('year')
    status = request.GET.get('status')
    popular = request.GET.get('popular')

    if author:
        books = books.filter(author_id=author)
    if genre:
        books = books.filter(genre_id=genre)
    if year:
        books = books.filter(year_published=year)
    if status:
        books = books.filter(status=status)
    if popular:
        books = books.filter(featured=popular)

    # صفحه‌بندی
    paginator = Paginator(books, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'library/Books.html', {
        'popular': ['popular', 'featured', 'normal'],
        'books': books,
        'page_obj': page_obj,
        'genres': Genre.objects.all(),
        'authors': Author.objects.all(),
        'years': Book.objects.values_list('year_published', flat=True).distinct(),
        'statuses': ['exist', 'sold', 'borrowed']
    })

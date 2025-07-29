from sys import maxsize

from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractUser
from django.conf import settings
from django_jalali.db import models as jmodels


class CustomUserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    STATUS = (
        ('regular', 'regular'),
        ('subscriber', 'subscriber'),
        ('moderator', 'moderator'),
    )
    fullname = models.CharField(max_length=200)
    email = models.EmailField( max_length=255, unique=True)
    is_admin = models.BooleanField(default=False,)
    status = models.CharField(max_length=100, choices=STATUS, default='regular')
    is_superuser = models.BooleanField(default=False,)
    last_login = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False, )
    is_verified = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True, unique=True)

    # Use 'username' as the USERNAME_FIELD
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Add required fields here

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value

class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    STATUS = (
        ('borrowed', 'borrowed'),
        ('sold', 'sold'),
        ('exist', 'exist'),
    )
    STATUSS = (
        ('normal', 'normal'),
        ('featured', 'featured'),
        ('popular', 'popular'),
    )
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    year_published = models.IntegerField()
    status = models.CharField(choices=STATUS , default='exist', max_length=25)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    discounted_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField(max_length=500 , blank=True , null=True )
    image = models.ImageField(upload_to='books/', blank=True , null=True )
    featured = models.CharField(choices=STATUSS , default='normal', max_length=25)


    def discount_percentage(self):
        if self.discounted_price and self.price > self.discounted_price:
            return round(100 - (self.discounted_price / self.price * 100))
        return 0

    def __str__(self):
        return self.title

class qoute(models.Model):
    qoute_of_day = models.CharField(max_length=500, blank=True, null=True)
    qoute_author = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.qoute_of_day

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, blank=True, null=True, unique=True)
    created_at = jmodels.jDateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبد های خرید'
        ordering = ['-created_at']


    class Meta:
        unique_together = ('user', 'session_key')

    def __str__(self):
        return f"Cart {self.id} - {self.user or 'Anonymous'}"



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Book', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = jmodels.jDateTimeField(auto_now_add=True)
    owned = models.BooleanField(default=False)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product.title}"

class Delivery(models.Model):
    method = models.CharField(max_length=40, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.method}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('draft', 'پیش‌نویس'),
        ('pending', 'در انتظار پرداخت'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = jmodels.jDateTimeField(auto_now_add=True,)
    payment_date = jmodels.jDateTimeField(null=True, blank=True)

    @classmethod
    def create_order(cls, user, items):
        if cls.objects.filter(user=user, created_at__gte=timezone.now() - timedelta(minutes=1)).count() > 3:
            raise ValidationError("امکان ثبت بیش از ۳ سفارش در دقیقه وجود ندارد")


    def save(self, *args, **kwargs):
        self.created_at_str = str(self.created_at)[:18]  # تبدیل به رشته و محدود کردن طول
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش #{self.id} - {self.get_status_display()}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Book', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.product.title}"


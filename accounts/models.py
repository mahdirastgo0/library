from random import choices

from django.db import models
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractUser
from django.shortcuts import redirect
from django.template.defaultfilters import slugify
import os
from django.core.exceptions import ValidationError
from django.utils.regex_helper import Choice
from django.contrib.auth import get_user_model


class UserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("وارد کردن ایمیل ضروری است.")
        if not username:
            raise ValueError("وارد کردن نام کاربری ضروری است.")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", False)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, email, password, **extra_fields)


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

    # Use 'username' as the USERNAME_FIELD
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Add required fields here

    objects = UserManager()

    def __str__(self):
        return self.username

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

class BookStatus(models.Model):
    STATUS = (
        ('borrowed', 'borrowed'),
        ('sold', 'sold'),
        ('exist', 'exist'),
    )
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(choices=STATUS , default='exist', max_length=25)

    def __str__(self):
        return self.status

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
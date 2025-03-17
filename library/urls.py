from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [

    path('', views.home, name='home'),
    path("library/", views.library, name="library"),
    path("books/", views.books, name="books"),

]
from django.shortcuts import render, redirect
from accounts.models import Book, Genre, qoute


def home(request):
    best_sellers = Book.objects.filter(status="sold").order_by("-price")[:1]
    featured_books = Book.objects.filter(featured="featured").order_by("-year_published")[:4]
    popular_books = Book.objects.filter(featured="popular").order_by("-year_published")[:4]

    # Get distinct genres, ensuring they are ordered correctly
    genres = Genre.objects.all()

    # Handle genre filtering (case-insensitive)
    selected_genre = request.GET.get("genre", "").strip()
    books = Book.objects.filter(genre__name__iexact=selected_genre) if selected_genre else Book.objects.all()
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
    return render(request,'library/library.html')

def books(request):
    return render(request,'library/books.html')




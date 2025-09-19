from django.shortcuts import render, get_object_or_404
from books.models import Book


def books_list(request):
    template = "books/books_list.html"
    books = Book.objects.all().order_by("pub_date")
    context = {"books": books}
    return render(request, template, context)


def books_by_date(request, pub_date):
    template = "books/books_by_date.html"
    # Все книги этой даты
    books = Book.objects.filter(pub_date=pub_date).order_by("name")

    # Все уникальные даты в отсортированном порядке
    dates = list(
        Book.objects.order_by("pub_date").values_list("pub_date", flat=True).distinct()
    )

    current_index = dates.index(books[0].pub_date) if books else -1

    prev_date = dates[current_index - 1] if current_index > 0 else None
    next_date = dates[current_index + 1] if current_index < len(dates) - 1 else None

    context = {
        "books": books,
        "current_date": pub_date,
        "prev_date": prev_date,
        "next_date": next_date,
    }
    return render(request, template, context)

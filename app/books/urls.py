from django.urls import path

from . import views

urlpatterns = [
    # BookCase URLs
    path("bookcases/", views.BookCaseListView.as_view(), name="bookcase-list"),
    path(
        "bookcases/<int:pk>/",
        views.BookCaseDetailView.as_view(),
        name="bookcase-detail",
    ),
    path("bookcases/new/", views.BookCaseCreateView.as_view(), name="bookcase-create"),
    path(
        "bookcases/<int:pk>/edit/",
        views.BookCaseUpdateView.as_view(),
        name="bookcase-update",
    ),
    path(
        "bookcases/<int:pk>/delete/",
        views.BookCaseDeleteView.as_view(),
        name="bookcase-delete",
    ),
    # BookShelf URLs (nested under BookCase)
    path(
        "shelves/<int:pk>/",
        views.BookShelfDetailView.as_view(),
        name="bookshelf-detail",
    ),
    path(
        "bookcases/<int:bookcase_pk>/shelves/new/",
        views.BookShelfCreateView.as_view(),
        name="bookshelf-create",
    ),
    path(
        "bookcases/<int:bookcase_pk>/shelves/<int:pk>/edit/",
        views.BookShelfUpdateView.as_view(),
        name="bookshelf-update",
    ),
    path(
        "shelves/<int:pk>/delete/",
        views.BookShelfDeleteView.as_view(),
        name="bookshelf-delete",
    ),
    # Book URLs
    path("books/", views.BookListView.as_view(), name="book-list"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book-detail"),
    path("books/new/", views.BookCreateView.as_view(), name="book-create"),
    path("books/<int:pk>/edit/", views.BookUpdateView.as_view(), name="book-update"),
    path("books/<int:pk>/delete/", views.BookDeleteView.as_view(), name="book-delete"),
    path("isbn/", views.ISBN.as_view()),
    path("books/new/isbn/", views.AddByISBNView.as_view(), name="book-create-isbn"),
    path("books/new/url/", views.AddByURLView.as_view(), name="book-create-url"),
    path("books/new/manual/", views.ManualEntryView.as_view(), name="book-create-manual"),
]

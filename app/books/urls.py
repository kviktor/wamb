from django.urls import path

from . import views

urlpatterns = [
    # Bookcase URLs
    path("bookcases/", views.BookcaseListView.as_view(), name="bookcase-list"),
    path("bookcases/new/", views.BookcaseCreateView.as_view(), name="bookcase-create"),
    path(
        "bookcases/<int:pk>/",
        views.BookcaseUpdateView.as_view(),
        name="bookcase-update",
    ),
    path(
        "bookcases/<int:pk>/delete/",
        views.BookcaseDeleteView.as_view(),
        name="bookcase-delete",
    ),
    # Book URLs
    path("books/", views.BookListView.as_view(), name="book-list"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book-detail"),
    path("books/new/", views.BookCreateView.as_view(), name="book-create"),
    path("books/<int:pk>/edit/", views.BookUpdateView.as_view(), name="book-update"),
    path("books/<int:pk>/delete/", views.BookDeleteView.as_view(), name="book-delete"),
    path("books/new/isbn/", views.AddByISBNView.as_view(), name="book-create-isbn"),
    path("books/new/url/", views.AddByURLView.as_view(), name="book-create-url"),
    path("books/new/manual/", views.ManualEntryView.as_view(), name="book-create-manual"),
    path("api/v1/autocomplete/", views.autocomplete),
]

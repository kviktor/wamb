from django import forms
from django.core.exceptions import ValidationError

from .models import Book, BookShelf


class AddByISBNForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("shelf", "isbn")

    def clean(self):
        data = self.cleaned_data

        isbn = data.get("isbn")
        if not isbn:
            raise ValidationError({"isbn": "This field is required."})

        if not str(isbn).isdigit():
            raise ValidationError({"isbn": "ISBN must only contain numbers."})

        if len(isbn) not in (10, 13):
            raise ValidationError({"isbn": "ISBN must be either 10 or 13 characters."})

        if Book.objects.filter(isbn=isbn).exists():
            raise ValidationError({"isbn": "A book with this ISBN already exists."})

        from app.metadata.services import get_book_by_isbn

        book = get_book_by_isbn(isbn)
        if not book:
            raise ValidationError({"isbn": "No book with that isbn."})

        self.book = book

    def save(self):
        from app.books.utils import create_book_object_from_pydantic

        book = create_book_object_from_pydantic(self.book)
        book.shelf = self.cleaned_data["shelf"]
        return book


class ManualEntryForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("shelf", "title", "authors", "isbn", "publication_year", "position")


class AddByURLForm(forms.Form):
    url = forms.URLField()
    shelf = forms.ModelChoiceField(queryset=BookShelf.objects.all(), required=False)

    def clean(self):
        data = self.cleaned_data

        url = data.get("url")
        if not url:
            raise ValidationError({"url": "This field is required."})

        from app.metadata.services import get_book_by_url

        book = get_book_by_url(url)
        if not book:
            raise ValidationError({"url": "Could not fetch book data from this URL."})

        self.book = book

    def save(self):
        from app.books.utils import create_book_object_from_pydantic

        return create_book_object_from_pydantic(self.book)

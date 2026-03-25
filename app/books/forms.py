from django import forms
from django.core.exceptions import ValidationError

from app.books.models import (
    Book,
    Bookcase,
    BookShelf,
)
from app.books.utils import create_book_object_from_pydantic
from app.metadata.services import (
    get_book_by_isbn,
    get_book_by_url,
)


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

        book = get_book_by_isbn(isbn)
        if not book:
            raise ValidationError({"isbn": "No book with that isbn."})

        self.book = book

    def save(self):
        book = create_book_object_from_pydantic(self.book)
        book.shelf = self.cleaned_data["shelf"]
        return book


class ManualEntryForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("shelf", "title", "authors", "isbn", "publication_year")


class AddByURLForm(forms.Form):
    url = forms.URLField()
    shelf = forms.ModelChoiceField(queryset=BookShelf.objects.all(), required=False)

    def clean(self):
        data = self.cleaned_data

        url = data.get("url")
        if not url:
            raise ValidationError({"url": "This field is required."})

        book = get_book_by_url(url)
        if not book:
            raise ValidationError({"url": "Could not fetch book data from this URL."})

        self.book = book

    def save(self):
        return create_book_object_from_pydantic(self.book)


class BookcaseCreateForm(forms.ModelForm):
    config = forms.JSONField()

    class Meta:
        model = Bookcase
        fields = ("name", "description", "rows", "columns", "config")

    def save(self, *args, **kwargs):
        bookcase = super().save(*args, **kwargs)

        shelves = []
        for row in self.cleaned_data["config"]:
            for cell in row:
                shelves.append(
                    BookShelf(
                        bookcase=bookcase,
                        row=cell["row"],
                        column=cell["col"],
                        config={
                            "rowspan": cell["rowspan"],
                            "colspan": cell["colspan"],
                        },
                    )
                )

        BookShelf.objects.bulk_create(shelves)

        return bookcase

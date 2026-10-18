from django import forms
from django.core.exceptions import ValidationError

from app.books.models import (
    Book,
    Bookcase,
    BookShelf,
)
from app.books.utils import create_book_object_from_pydantic
from app.books.widgets import AutocompleteSelectMultiple
from app.metadata.services import (
    get_book_by_isbn,
    get_book_by_url,
)


class BookSaveMixin:
    def save(self):
        book = create_book_object_from_pydantic(self.book)

        if shelf := self.cleaned_data["shelf"]:
            book.shelf = shelf
            book.position = book.shelf.get_next_position()

        book.save(update_fields=["shelf", "position"])

        return book


def validate_isbn(isbn, field_name="isbn", *, unique_check: bool):
    # replace/ignore dashes and whitespaces
    isbn = isbn.replace("-", "").replace(" ", "").upper()

    # technically a checksum check would be required for a proper validity
    # but there are books out with invalid isbn too
    if len(isbn) == 10:
        if not (isbn[:-1].isdigit() and (isbn[-1].isdigit() or isbn[-1] == "X")):
            raise ValidationError({field_name: "Invalid ISBN."})
    elif len(isbn) == 13:
        if not isbn.isdigit():
            raise ValidationError({field_name: "ISBN must only contain numbers."})
    else:
        raise ValidationError({field_name: "ISBN must be either 10 or 13 characters."})

    if unique_check and Book.objects.filter(isbn=isbn).exists():
        raise ValidationError({field_name: "A book with this ISBN already exists."})


class AddByISBNForm(BookSaveMixin, forms.ModelForm):
    class Meta:
        model = Book
        fields = ("shelf", "isbn")

    def clean(self):
        data = self.cleaned_data

        isbn = data.get("isbn")
        if not isbn:
            raise ValidationError({"isbn": "This field is required."})

        validate_isbn(isbn, unique_check=True)

        book = get_book_by_isbn(isbn)
        if not book:
            raise ValidationError({"isbn": "No book with that isbn."})

        self.book = book


class ManualEntryForm(forms.ModelForm):
    """also used for BookUpdateView"""

    class Meta:
        model = Book
        fields = (
            "shelf",
            "title",
            "authors",
            "isbn",
            "publication_year",
            "number_of_pages",
        )
        widgets = {"authors": AutocompleteSelectMultiple(model="author")}

    def clean(self):
        super().clean()
        if isbn := self.cleaned_data.get("isbn"):
            validate_isbn(isbn, unique_check=False)

    def save(self, *args, **kwargs):
        book = super().save(*args, **kwargs)

        if shelf := self.cleaned_data["shelf"]:
            book.shelf = shelf
            book.position = book.shelf.get_next_position()

        book.save(update_fields=["shelf", "position"])

        return book


class AddByURLForm(BookSaveMixin, forms.Form):
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

        if book.isbn:
            validate_isbn(book.isbn, field_name="url", unique_check=True)

        self.book = book


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

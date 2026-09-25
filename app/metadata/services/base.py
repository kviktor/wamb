from datetime import date
import importlib

from pydantic import BaseModel

from app.metadata.models import ISBNLookup


class AuthorMetadata(BaseModel):
    name: str
    gender: str
    country: str
    birth_date: date | None
    third_party_data: dict


class BookMetadata(BaseModel):
    isbn: str
    title: str
    authors: list[AuthorMetadata]
    publication_year: int | None
    number_of_pages: int | None
    cover_url: str | None
    third_party_data: dict

    @property
    def has_all_info(self) -> bool:
        return bool(
            self.isbn
            and self.title
            and self.cover_url
            and self.publication_year
            and self.number_of_pages
        )

    @property
    def has_enough_info(self) -> bool:
        return bool(self.isbn and self.title and self.authors)

    def merge(self, book: BookMetadata) -> BookMetadata:
        fields = ("title", "authors", "publication_year", "number_of_pages", "cover_url")
        for field in fields:
            new_value = getattr(book, field)
            if new_value and not getattr(self, field):
                setattr(self, field, new_value)

        self.third_party_data |= book.third_party_data

        return self


def get_book_by_isbn(isbn: str) -> BookMetadata | None:
    try:
        book = BookMetadata(**ISBNLookup.objects.get(isbn=isbn).serialized_data)
    except ISBNLookup.DoesNotExist:
        book = {}

    if book:
        return book

    services = get_service_names()

    base_book = None
    for service_name in services:
        service = get_service(service_name)
        book = service.get_book_by_isbn(isbn)

        if not base_book:
            base_book = book
        elif book:
            base_book = base_book.merge(book)

        # if we have all the required information we should stop querying other services
        if base_book and base_book.has_all_info:
            ISBNLookup.objects.create(isbn=isbn, serialized_data=base_book.model_dump())
            return base_book

    # if we have enough info (title, isbn, authors) we should still create a lookup object
    if base_book and base_book.has_enough_info:
        ISBNLookup.objects.create(isbn=isbn, serialized_data=base_book.model_dump())

    return base_book


def get_book_by_url(url: str) -> BookMetadata | None:
    for service_name in get_service_names():
        service = get_service(service_name)
        if service.SUPPORTS_URL and service.URL_PATTERN.match(url):
            return service.get_book_by_url(url)

    return None


def get_service_names() -> list[str]:
    from app.metadata.models import Service

    return [
        Service.moly.name,
        Service.openlibrary.name,
        Service.google_books.name,
    ]


def get_service(service_name: str):
    return importlib.import_module(f"app.metadata.services.{service_name}")

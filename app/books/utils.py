from mimetypes import guess_extension
from pathlib import Path
import urllib
import uuid

from django.core.files.base import ContentFile

from app.books.models import Author, Book, Image
from app.metadata.models import Service
from app.metadata.services.base import BookMetadata
from app.metadata.services.client import Client


class ImageClient(Client):
    SERVICE = Service.image


def get_or_create_image(cover_url: str) -> Image | None:
    if not cover_url:
        return None

    if image := Image.objects.filter(source=cover_url).first():
        return image

    # download image
    response = ImageClient().get(cover_url)
    content_file = ContentFile(response.content)
    image = Image(source=cover_url)

    # generate the name from the cover url
    name = Path(urllib.parse.urlparse(cover_url).path).name

    # it might not contain an extension (Google Books for example)
    if "." not in name:
        content_type = response.headers["Content-Type"]
        ext = guess_extension(content_type)
        name = f"{uuid.uuid4()}{ext}"

    image.image.save(name, content_file, save=True)

    return image


def create_book_object_from_pydantic(book: BookMetadata) -> Book:
    image: Image | None = get_or_create_image(book.cover_url)

    db_book = Book.objects.create(
        title=book.title,
        cover=image,
        publication_year=book.publication_year,
        number_of_pages=book.number_of_pages,
        isbn=book.isbn,
        third_party_data=book.third_party_data,
    )

    authors = []

    for author in book.authors:
        obj, created = Author.objects.get_or_create(
            name=author.name,
            defaults={
                "third_party_data": author.third_party_data,
            },
        )

        # we might have extra third_party data
        if not created and obj.third_party_data != author.third_party_data:
            obj.third_party_data = {
                **obj.third_party_data,
                **author.third_party_data,
            }
            obj.save(update_fields=["third_party_data"])

        authors.append(obj)

    db_book.authors.set(authors)

    return db_book

from io import BytesIO
from mimetypes import guess_extension
from pathlib import Path
import urllib
import uuid

from PIL import Image as PillowImage

from django.core.files.base import ContentFile

from app.books.models import Author, Book, Image
from app.metadata.models import Service
from app.metadata.services.base import BookMetadata
from app.metadata.services.client import Client


class ImageClient(Client):
    SERVICE = Service.image


def get_or_create_image(image_url: str) -> Image | None:
    if not image_url:
        return None

    # in case the image url is too long
    truncated_image_url = image_url[:200]

    if image := Image.objects.filter(source=truncated_image_url).first():
        return image

    # download image
    response = ImageClient().get(image_url)
    content_file = ContentFile(response.content)
    image = Image(source=truncated_image_url)

    # generate the name from the cover url
    name = Path(urllib.parse.urlparse(image_url).path).name

    # it might not contain an extension (Google Books for example)
    if "." not in name:
        content_type = response.headers["Content-Type"]
        ext = guess_extension(content_type)
        name = f"{uuid.uuid4()}{ext}"

    if len(name) > 90:
        ext = Path(name).suffix
        name = f"{name[:90]}{ext}"

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

        if created:
            from app.metadata.services.wikidata import update_author

            update_author(obj)

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


def get_int_or_default(value, default=None):
    try:
        return int(value)
    except TypeError, ValueError:
        return default


def convert_and_resize_image(image_file, width: int = None):
    pillow_image = PillowImage.open(image_file)

    if width and pillow_image.width > width:
        ratio = pillow_image.width / width
        height = int(pillow_image.height / ratio)
        pillow_image = pillow_image.resize((width, height))

    buffer = BytesIO()
    pillow_image.save(buffer, "webp", method=4, quality=90)
    pillow_image.close()

    return buffer

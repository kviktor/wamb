import re

from app.metadata.models import Service
from app.metadata.services.base import AuthorMetadata, BookMetadata
from app.metadata.services.client import Client

SUPPORTS_ISBN = True
SUPPORTS_URL = False
URL_PATTERN = None


class GoogleClient(Client):
    SERVICE = Service.google_books

    def get_book(self, isbn: str) -> dict | None:
        url = (
            f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            f"&fields=items/id,items/volumeInfo(title,subtitle,authors,publisher,publishedDate,"
            f"language,industryIdentifiers,description,imageLinks,pageCount)&maxResults=1"
        )
        response = self.get(url)
        if not response:
            return None

        response_data = response.json()
        if not (response_data and response_data.get("items")):
            return None

        data = response_data["items"][0]
        # sanity ISBN check
        identifiers = [
            row["identifier"]
            for row in data.get("volumeInfo", {}).get("industryIdentifiers", [])
        ]
        if isbn not in identifiers:
            # TODO proper log
            raise ValueError("Got a result back with different ISBN")

        return data


def parse_year(date_string: str) -> int | None:
    if match := re.search(r"\d{4}", date_string):
        return int(match.group())

    return None


def get_book_by_isbn(isbn: str) -> BookMetadata | None:
    data = GoogleClient().get_book(isbn)
    if not data:
        return None

    volume_info = data["volumeInfo"]
    image_links = volume_info.get("imageLinks", {})

    return BookMetadata(
        isbn=isbn,
        title=volume_info["title"],
        authors=[
            AuthorMetadata(
                name=author,
                birth_date=None,
                third_party_data={},
            )
            for author in volume_info["authors"]
        ],
        publication_year=parse_year(volume_info.get("publishedDate")),
        number_of_pages=volume_info.get("pageCount"),
        third_party_data={
            "google_books": {"id": data.get("id")},
        },
        cover_url=image_links.get("thumbnail") or image_links.get("smallThumbnail"),
    )

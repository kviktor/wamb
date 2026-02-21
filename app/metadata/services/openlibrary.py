from app.metadata.models import Service
from app.metadata.services.base import AuthorMetadata, BookMetadata
from app.metadata.services.client import Client

SUPPORTS_ISBN = True
SUPPORTS_URL = False
URL_PATTERN = None


class OpenLibraryClient(Client):
    BASE_URL = "https://openlibrary.org"
    SERVICE = Service.openlibrary

    def get_book(self, isbn: str) -> dict | None:
        url = f"{self.BASE_URL}/isbn/{isbn}.json"
        response = self.get(url)
        if not response:
            return None

        return response.json()

    def get_author(self, olid: str) -> dict | None:
        url = f"{self.BASE_URL}/authors/{olid}.json"
        response = self.get(url)
        if not response:
            return None

        return response.json()

    def get_cover_url(self, olid: str) -> str | None:
        cover_url = f"https://covers.openlibrary.org/b/olid/{olid}-L.jpg"
        if self.head(cover_url, params={"default": "false"}):
            return cover_url
        else:
            return None


def get_olid(olid):
    return olid.split("/")[-1]


def parse_year(raw_date: str) -> int | None:
    if not raw_date:
        return None

    last_4 = raw_date[:-4]
    if last_4.isdigit():
        return int(last_4)

    return None


def get_book_by_isbn(isbn: str) -> BookMetadata | None:
    client = OpenLibraryClient()
    data = client.get_book(isbn)
    if not data:
        return None

    olid = get_olid(data["key"])

    return BookMetadata(
        isbn=isbn,
        title=data.get("full_title") or data.get("title"),
        authors=[
            AuthorMetadata(
                name=author_data["name"],
                birth_date=parse_year(author_data.get("birth_date")),
                third_party_data={
                    "openlibrary": {
                        "olid": get_olid(author_data["key"]),
                    },
                },
            )
            for author in data["authors"]
            if (author_data := client.get_author(get_olid(author["key"])))
        ],
        publication_year=parse_year(data.get("publication_year")),
        number_of_pages=data.get("number_of_pages"),
        cover_url=client.get_cover_url(olid),
        third_party_data={"openlibrary": {"olid": olid}},
    )

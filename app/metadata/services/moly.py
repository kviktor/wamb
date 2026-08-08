import re

from bs4 import BeautifulSoup

from app.metadata.models import Service
from app.metadata.services.base import AuthorMetadata, BookMetadata
from app.metadata.services.client import Client

SUPPORTS_ISBN = True
SUPPORTS_URL = True
URL_PATTERN = re.compile(r"https?://(www\.)?moly\.hu/kiadasok/\d+")


class MolyClient(Client):
    BASE_URL = "https://moly.hu"
    SERVICE = Service.moly

    def get_headers(self):
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
            ),
        }

    def _get_book_url(self, isbn: str):
        params = {
            "utf8": "✓",
            "query": isbn,
        }
        search_response = self.get("https://moly.hu/kereses", params=params)

        search_soup = BeautifulSoup(search_response.content, "html.parser")
        table_cells = search_soup.find("div", id="content").find_all("td")
        if not table_cells:
            return None

        p_tags = table_cells[0].find_all("p")
        if not p_tags:
            return None

        href = p_tags[0].find("a").attrs["href"]
        return f"https://moly.hu{href}"

    def _get_edition_url(self, book_url, isbn) -> tuple[str | None, dict]:
        data = {}
        book_response = self.get(book_url)
        book_soup = BeautifulSoup(book_response.content, "html.parser")

        div_content = book_soup.find("div", id="content")
        head = div_content.find_all("div", class_="head")[0]
        div_authors = head.find_all("div", class_="authors")[0]
        authors = []
        for author in div_authors.find_all("a"):
            href = author["href"]
            name = author.text
            authors.append(
                {
                    "link": f"https://moly.hu{href}",
                    "name": name,
                    "slug": href.replace("/alkotok/", ""),
                },
            )

        title = div_content.find("h1").find_all("span", class_="item")[0].text

        editions = div_content.find_all("div", id=re.compile(r"^edition_\d+"))
        filtered_editions = [edition for edition in editions if isbn in str(edition)]
        if not filtered_editions:
            return None, {}

        edition = filtered_editions[0]
        edition_id = int(edition.attrs["id"].replace("edition_", ""))
        edition_href = edition.find_all("a", href=re.compile(r"^/kiadasok/\d+"))[0].attrs[
            "href"
        ]

        data = {
            "authors": authors,
            "title": title,
            "edition_id": edition_id,
            "book_slug": book_url.replace("https://moly.hu/konyvek/", ""),
        }

        return f"https://moly.hu{edition_href}", data

    def _parse_number(self, value: str) -> int | None:
        try:
            return int(value)
        except TypeError, ValueError:
            return None

    def _get_edition_data(self, edition_url: str, edition_response: str = "") -> dict:
        data = {
            "publication_year": None,
            "number_of_pages": None,
            "cover_url": None,
        }

        if not edition_response:
            edition_response = self.get(edition_url)

        edition_soup = BeautifulSoup(edition_response.content, "html.parser")

        # get the cover image
        div_cover = edition_soup.find_all("div", class_="covers")[0]
        img_tags = div_cover.find_all("img")
        if img_tags:
            data["cover_url"] = img_tags[0].attrs["src"].replace("/normal/", "/big/")

        div_content = edition_soup.find("div", class_="flex_content")
        if div_content:
            ul = div_content.find("ul")
            if ul:
                for li in ul.find_all("li"):
                    pairs = (
                        ("publication_year", "Kiadás éve"),
                        ("number_of_pages", "Oldalszám"),
                    )
                    for name, text in pairs:
                        if text in str(li):
                            value = self._parse_number(li.find("strong").text)
                            data[name] = value

        return data

    def get_book_by_isbn(self, isbn: str):
        book_url = self._get_book_url(isbn)
        if not book_url:
            return None

        edition_url, data = self._get_edition_url(book_url, isbn)
        if not edition_url:
            return None

        data["isbn"] = isbn
        data.update(self._get_edition_data(edition_url))

        return data

    def get_book_by_url(self, url: str):
        response = self.get(url)
        edition_soup = BeautifulSoup(response, "html.parser")

        div_content = edition_soup.find("div", class_="flex_content")
        if not div_content:
            return None

        ul = div_content.find("ul")
        if ul:
            for li in ul.find_all("li"):
                if "ISBN" in str(li):
                    isbn = li.find("strong").text
                    return self.get_book_by_isbn(isbn)

        # edition has no ISBN, extract rest of the information

        # find the main book url to get title + authors
        book_url = edition_soup.find_all(
            "a", href=re.compile(r"^/konyvek/[0-9a-zA-Z_\.-]+")
        )[0].attrs["href"]

        # TODO fix this duplication
        book_response = self.get(f"https://moly.hu{book_url}")
        book_soup = BeautifulSoup(book_response.content, "html.parser")

        div_content = book_soup.find("div", id="content")
        head = div_content.find_all("div", class_="head")[0]
        div_authors = head.find_all("div", class_="authors")[0]
        authors = []
        for author in div_authors.find_all("a"):
            href = author["href"]
            name = author.text
            authors.append(
                {
                    "link": f"https://moly.hu{href}",
                    "name": name,
                    "slug": href.replace("/alkotok/", ""),
                },
            )

        title = div_content.find("h1").find_all("span", class_="item")[0].text

        data = {
            "isbn": "",
            "authors": authors,
            "title": title,
            "edition_id": url.replace("https://moly.hu/kiadasok/", ""),
            "book_slug": book_url.removeprefix("/konyvek"),
            # get edition data from the same content so we only have 2x queries
            **self._get_edition_data(None, response),
        }

        return data


def _get_book(data: dict) -> BookMetadata:
    return BookMetadata(
        isbn=data["isbn"],
        title=data["title"],
        authors=[
            AuthorMetadata(
                name=author_data["name"],
                gender="",
                country="",
                birth_date=None,
                third_party_data={
                    "moly_slug": author_data["slug"],
                },
            )
            for author_data in data["authors"]
        ],
        publication_year=data["publication_year"],
        number_of_pages=data["number_of_pages"],
        cover_url=data["cover_url"],
        third_party_data={
            "moly": {"edition_id": data["edition_id"], "book_slug": data["book_slug"]}
        },
    )


def get_book_by_url(url: str) -> BookMetadata | None:
    client = MolyClient()
    data = client.get_book_by_url(url)
    if not data:
        return None

    return _get_book(data)


def get_book_by_isbn(isbn: str):
    client = MolyClient()
    data = client.get_book_by_isbn(isbn)
    if not data:
        return None

    return _get_book(data)

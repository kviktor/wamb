from model_bakery import baker

from django.test import TestCase

from app.books import (
    models,
    utils,
)
from app.metadata.services.base import (
    AuthorMetadata,
    BookMetadata,
)


class CreateBookObjectFromPydantic(TestCase):
    def setUp(self):
        self.metadata = BookMetadata(
            isbn="",
            title="t",
            cover_url=None,
            third_party_data={},
            authors=[
                AuthorMetadata(
                    name="author name", birth_date=None, third_party_data={"3rd": "yes"}
                )
            ],
            publication_year=None,
            number_of_pages=None,
        )

    def test_new_author(self):
        utils.create_book_object_from_pydantic(self.metadata)

        author = models.Author.objects.get(name="author name")
        self.assertEqual(author.third_party_data, {"3rd": "yes"})

    def test_existing_author(self):
        author = baker.make(
            models.Author, name="author name", third_party_data={"3rd": "yes"}
        )

        book = utils.create_book_object_from_pydantic(self.metadata)

        self.assertEqual(author, book.authors.get())

    def test_same_author_different_third_party(self):
        author = baker.make(
            models.Author, name="author name", third_party_data={"another": "one"}
        )

        utils.create_book_object_from_pydantic(self.metadata)

        author.refresh_from_db()
        self.assertEqual(
            author.third_party_data,
            {
                "3rd": "yes",
                "another": "one",
            },
        )

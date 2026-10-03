from unittest import mock

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
                    name="author name",
                    gender="",
                    country="",
                    birth_date=None,
                    third_party_data={"3rd": "yes"},
                )
            ],
            publication_year=None,
            number_of_pages=None,
        )
        patcher = mock.patch("app.metadata.services.wikidata.update_author")
        self.p_update_author = patcher.start()
        self.addCleanup(patcher.stop)

    def test_new_author(self):
        utils.create_book_object_from_pydantic(self.metadata)

        author = models.Author.objects.get(name="author name")
        self.assertEqual(author.third_party_data, {"3rd": "yes"})
        self.p_update_author.assert_called_once_with(author)

    def test_existing_author(self):
        author = baker.make(
            models.Author, name="author name", third_party_data={"3rd": "yes"}
        )

        book = utils.create_book_object_from_pydantic(self.metadata)

        self.assertEqual(author, book.authors.get())
        self.p_update_author.assert_not_called()

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
        self.p_update_author.assert_not_called()

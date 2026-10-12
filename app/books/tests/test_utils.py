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


class GetOrCreateImageTest(TestCase):
    def test_empty_url(self):
        self.assertIsNone(utils.get_or_create_image(""))

    def test_already_in_db(self):
        image = baker.make("books.Image", source="http://te.st/image.jpeg")
        self.assertEqual(utils.get_or_create_image("http://te.st/image.jpeg"), image)

    def test_already_in_db_too_long(self):
        long_source = "http://" + "a" * 200
        image = baker.make("books.Image", source="http://" + "a" * (200 - len("http://")))
        self.assertEqual(utils.get_or_create_image(long_source), image)

    @mock.patch("app.books.utils.ImageClient.get")
    def test_name_too_long(self, p_get):
        response = mock.Mock(content=b"")
        response.headers = {}
        p_get.return_value = response
        long_source = "http://te.st/" + "a" * 200 + ".jpg"

        image = utils.get_or_create_image(long_source)
        self.assertEqual(image.image.name, "a" * 90 + ".jpg")


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

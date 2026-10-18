from unittest import mock

from model_bakery import baker
from parameterized import parameterized

from django.core.exceptions import ValidationError
from django.test import TestCase

from app.books import forms


class AddByISBNFormTest(TestCase):
    @mock.patch("app.books.forms.get_book_by_isbn")
    @mock.patch("app.books.forms.create_book_object_from_pydantic")
    def test_save_no_shelf(self, p_create, p_get):
        p_get.return_value = "pydantic book object"
        book = baker.make("books.Book", shelf=None)
        p_create.return_value = book

        form = forms.AddByISBNForm({"isbn": 1_000_000_000_000})

        self.assertTrue(form.is_valid())
        form.save()
        self.assertIsNone(book.shelf)
        self.assertEqual(book.position, 0)

    @mock.patch("app.books.forms.get_book_by_isbn")
    @mock.patch("app.books.forms.create_book_object_from_pydantic")
    def test_save_with_shelf(self, p_create, p_get):
        p_get.return_value = "pydantic book object"
        book = baker.make("books.Book", shelf=None)
        p_create.return_value = book
        shelf = baker.make("books.BookShelf")

        form = forms.AddByISBNForm({"isbn": 1_000_000_000_000, "shelf": shelf.pk})

        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(book.shelf, shelf)
        self.assertEqual(book.position, 0)


class ValidateISBNTest(TestCase):
    @parameterized.expand(
        [
            [""],
            ["X123456789"],
            ["123456789Z"],
            ["123456789012X"],
            ["12345678901234"],
            ["123456789"],
            ["12345678901"],
        ],
    )
    def test_invalid(self, value):
        with self.assertRaises(ValidationError):
            forms.validate_isbn(value, unique_check=False)

    @parameterized.expand(
        [
            ["123456789X"],
            ["1234567890123"],
        ],
    )
    def test_valid(self, value):
        forms.validate_isbn(value, unique_check=False)

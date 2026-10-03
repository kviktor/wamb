from unittest import mock

from model_bakery import baker

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

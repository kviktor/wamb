from parameterized import parameterized

from django.test import TestCase

from app.books import models


class BookShelfTest(TestCase):
    @parameterized.expand(
        [
            (0, 0, "A1"),
            (0, 25, "Z1"),
            (0, 26, "AA1"),
            (0, 51, "AZ1"),
            (0, 52, "BA1"),
            (0, 77, "BZ1"),
            (0, 78, "CA1"),
            (0, 16383, "XFD1"),
        ]
    )
    def test_location_letters(self, row, column, expected):
        shelf = models.BookShelf(row=row, column=column, bookcase=models.Bookcase(rows=1))
        self.assertEqual(shelf.location, expected)

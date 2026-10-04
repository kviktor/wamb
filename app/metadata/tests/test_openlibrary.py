from datetime import date

from parameterized import parameterized

from django.test import TestCase

from app.metadata.services import openlibrary


class ParseYearTest(TestCase):
    @parameterized.expand(
        [
            ("31 July 1965", 1965),
            ("1935?", 1935),
            ("2010-10-10", 2010),
            ("08/08/2016", 2016),
            ("", None),
            ("aint int", None),
        ]
    )
    def test_function(self, raw_data, expected):
        self.assertEqual(openlibrary.parse_year(raw_data), expected)


class ParseDateTest(TestCase):
    @parameterized.expand(
        [
            ("31 July 1965", date(1965, 7, 31)),
            ("4 April 1948", date(1948, 4, 4)),
            ("1935?", date(1935, 1, 1)),
            ("2010-10-10", date(2010, 1, 1)),
            ("08/08/2016", date(2016, 1, 1)),
            ("", None),
            ("aint int", None),
        ]
    )
    def test_function(self, raw_data, expected):
        self.assertEqual(openlibrary.parse_date(raw_data), expected)

from unittest import mock

from model_bakery import baker
from parameterized import parameterized

from django.test import TestCase

from app.metadata.services import wikidata


class UpdateAuthorTest(TestCase):
    @parameterized.expand(
        [
            ("+1564-04-00T00:00:00Z", (1564, 4, 1)),
            ("+1564-00-00T00:00:00Z", (1564, 1, 1)),
            ("cantparsethis", None),
        ],
    )
    @mock.patch("app.metadata.services.wikidata.WikidataClient.search")
    def test_parse_date(self, time_text, date_tuple, p_search):
        p_search.return_value = {
            "claims": {
                "P569": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P569",
                            "hash": "b442d5a7a5dc320f2a8744f9abfa245c06ad1515",
                            "datavalue": {
                                "value": {
                                    "time": time_text,
                                    "timezone": 0,
                                    "before": 0,
                                    "after": 0,
                                    "precision": 10,
                                    "calendarmodel": "http://www.wikidata.org/entity/Q1985786",
                                },
                                "type": "time",
                            },
                            "datatype": "time",
                        },
                    }
                ]
            }
        }
        author = baker.make("books.Author", birth_date=None)

        if date_tuple:
            ctx = self.assertNoLogs()
        else:
            ctx = self.assertLogs()

        with ctx as cm:
            wikidata.update_author(author)

        if date_tuple:
            self.assertEqual(
                (author.birth_date.year, author.birth_date.month, author.birth_date.day),
                date_tuple,
            )
        else:
            self.assertIsNone(author.birth_date)
            self.assertIn("wikidata.invalid_birth_date", str(cm.output[0]))

    @mock.patch("app.metadata.services.wikidata.WikidataClient.search")
    def test_assert_no_date(self, p_search):
        p_search.return_value = {}
        author = baker.make("books.Author", birth_date=None)

        with self.assertNoLogs():
            wikidata.update_author(author)

        self.assertIsNone(author.birth_date)

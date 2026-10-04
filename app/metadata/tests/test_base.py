from django.test import (
    TestCase,
    override_settings,
)

from app.metadata.services import base


class GetServiceNamesTest(TestCase):
    @override_settings(METADATA_SERVICE_ORDER=["google_books", "openlibrary"])
    def test_order_set(self):
        self.assertEqual(base.get_service_names(), ["google_books", "openlibrary"])

    @override_settings(METADATA_SERVICE_ORDER=["google_books", "mamma mia"])
    def test_invalid_entry(self):
        self.assertEqual(base.get_service_names(), ["google_books"])

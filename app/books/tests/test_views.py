from model_bakery import baker

from django.test import TestCase
from django.urls import reverse


class SanityTest(TestCase):
    """quick test so all pages render"""

    def test_pages(self):
        user = baker.make("users.User", is_superuser=True)
        bookcase = baker.make("books.Bookcase", rows=1, columns=1)
        author = baker.make("books.Author")
        book = baker.make("books.Book")

        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200, "login")

        self.client.force_login(user)

        urls = [
            reverse("index"),
            reverse("book-list"),
            reverse("book-create"),
            reverse("book-detail", kwargs={"pk": book.pk}),
            reverse("book-update", kwargs={"pk": book.pk}),
            reverse("bookcase-list"),
            reverse("bookcase-create"),
            reverse("bookcase-detail", kwargs={"pk": bookcase.pk}),
            reverse("bookcase-update", kwargs={"pk": bookcase.pk}),
            reverse("author-list"),
            reverse("author-create"),
            reverse("author-detail", kwargs={"pk": author.pk}),
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)

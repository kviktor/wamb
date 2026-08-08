import itertools

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Image(TimeStampedModel):
    source = models.URLField(unique=True)
    image = models.ImageField(blank=True)

    def __str__(self):
        return self.source


class Author(TimeStampedModel):
    name = models.CharField(max_length=200)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=32, blank=True, default="")
    country = models.CharField(max_length=2, blank=True, default="")
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)

    third_party_data = models.JSONField(default=dict)

    def __str__(self):
        return self.name


class Bookcase(TimeStampedModel):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    rows = models.PositiveSmallIntegerField()
    columns = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

    @property
    def shelves_config(self):
        rows = []
        # sameish as `regroup`
        for row in itertools.groupby(self.shelves.all(), key=lambda x: x.row):
            rows.append(
                [
                    {
                        "id": shelf.id,
                        "location": shelf.location,
                        "row": shelf.row,
                        "col": shelf.column,
                        "rowspan": shelf.config.get("rowspan"),
                        "colspan": shelf.config.get("colspan"),
                        "selected": False,
                    }
                    for shelf in list(row[1])
                ],
            )
        return rows


class BookShelf(TimeStampedModel):
    bookcase = models.ForeignKey(
        Bookcase, on_delete=models.CASCADE, related_name="shelves"
    )
    name = models.CharField(max_length=128)

    row = models.PositiveSmallIntegerField(default=0)
    column = models.PositiveSmallIntegerField(default=0)

    config = models.JSONField(default=dict)

    class Meta:
        ordering = ("row", "column")

    def __str__(self):
        return f"{self.name} ({self.bookcase})"

    @property
    def location(self):
        column_name = ""

        column = self.column + 1
        while column > 0:
            modulo = (column - 1) % 26
            column_name = chr(ord("A") + modulo) + column_name
            column = (column - modulo) // 26

        row = self.bookcase.rows - self.row
        # rowspan is always set to 1
        if rowspan := self.config.get("rowspan"):
            row -= rowspan - 1

        return f"{column_name}{row}"


class Book(TimeStampedModel):
    shelf = models.ForeignKey(
        BookShelf,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="books",
    )
    title = models.CharField(max_length=300)
    cover = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    position = models.PositiveSmallIntegerField(
        default=0,
        help_text="Position of the book within the shelf. From left to right.",
    )
    authors = models.ManyToManyField(Author, blank=True, related_name="books")
    isbn = models.CharField(max_length=13, blank=True)
    publication_year = models.PositiveSmallIntegerField(blank=True, null=True)
    number_of_pages = models.PositiveSmallIntegerField(blank=True, null=True)

    third_party_data = models.JSONField(default=dict)

    added_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["isbn"], condition=~models.Q(isbn=""), name="unique_isbn_if_set"
            )
        ]

    def __str__(self):
        text = self.title

        if self.isbn:
            text = f"{text} ({self.isbn})"

        return text

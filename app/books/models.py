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


class BookShelf(TimeStampedModel):
    bookcase = models.ForeignKey(
        Bookcase, on_delete=models.CASCADE, related_name="shelves"
    )
    name = models.CharField(max_length=128)

    row = models.PositiveSmallIntegerField(default=0)
    column = models.PositiveSmallIntegerField(default=0)

    config = models.JSONField(default=dict)

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

        return f"{column_name}{self.row + 1}"


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

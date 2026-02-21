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


class BookCase(TimeStampedModel):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class BookShelf(TimeStampedModel):
    bookcase = models.ForeignKey(
        BookCase, on_delete=models.CASCADE, related_name="shelves"
    )
    name = models.CharField(max_length=200)
    vertical_position = models.IntegerField(
        default=0,
        help_text="Position of the shelf within the bookcase. 0 is ground level.",
    )
    horizontal_position = models.IntegerField(
        default=0,
        help_text="Position of the shelf within the bookcase. From left to right.",
    )

    def __str__(self):
        return f"{self.name} ({self.bookcase})"


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

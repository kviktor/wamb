from django.db import models


class ISBNLookup(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    serialized_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.isbn


class Service(models.IntegerChoices):
    openlibrary = 1
    moly = 2
    google_books = 3
    image = 4


class ResponseLog(models.Model):
    service = models.PositiveSmallIntegerField(choices=Service.choices)
    url = models.CharField(max_length=256)
    method = models.CharField(max_length=8)
    response = models.TextField()
    content_type = models.CharField(max_length=64)
    exc = models.TextField()
    status_code = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url

from django.contrib import admin

from .models import Author, Book, Bookcase, BookShelf, Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass


@admin.register(Bookcase)
class BookcaseAdmin(admin.ModelAdmin):
    pass


@admin.register(BookShelf)
class BookShelfAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass

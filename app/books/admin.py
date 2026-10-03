from django.contrib import admin

from .models import Author, Book, Bookcase, BookShelf, Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass


class BookInline(admin.TabularInline):
    model = Author.books.through
    fields = ("title",)
    readonly_fields = ("title",)
    can_delete = False
    can_add = False
    extra = 0

    def title(self, obj):
        return obj.book.title


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    inlines = [BookInline]


@admin.register(Bookcase)
class BookcaseAdmin(admin.ModelAdmin):
    list_display = ("name", "rows", "columns")


@admin.register(BookShelf)
class BookShelfAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    raw_id_fields = ("shelf", "cover", "authors", "added_by")
    list_display = ("id", "title", "isbn", "shelf", "added_by")

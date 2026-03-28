from django.contrib import admin

from app.metadata import models


@admin.register(models.ISBNLookup)
class ISBNLookupAdmin(admin.ModelAdmin):
    list_display = ("isbn", "title", "created_at")

    @admin.display
    def title(self, obj):
        return obj.serialized_data.get("title")


@admin.register(models.ResponseLog)
class ResponseLogAdmin(admin.ModelAdmin):
    list_display = ("service", "url", "method", "status_code", "created_at")

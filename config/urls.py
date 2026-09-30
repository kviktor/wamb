from django.conf import settings
from django.contrib import admin
from django.urls import (
    include,
    path,
    re_path,
)
from django.views.static import serve

from app.books import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("", include("app.books.urls")),
    path("", include("app.users.urls")),
]

if settings.SERVE_MEDIA_FILES:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {
                "document_root": settings.MEDIA_ROOT,
            },
        ),
    ]

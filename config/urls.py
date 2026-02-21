from django.conf import settings
from django.contrib import admin
from django.urls import (
    re_path,
    path,
    include,
)
from django.views.static import serve


from app.books import views

urlpatterns = [
    path("", views.IndexView.as_view()),
    path("admin/", admin.site.urls),
    path("", include("app.books.urls")),
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

from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import (
    AddByISBNForm,
    AddByURLForm,
    BookcaseCreateForm,
    ManualEntryForm,
)
from .models import Book, Bookcase, BookShelf


# TODO ignore for now
class IndexView(TemplateView):
    template_name = "index.html"


class BookcaseListView(ListView):
    model = Bookcase
    template_name = "books/bookcase_list.html"
    context_object_name = "bookcases"


class BookcaseCreateView(CreateView):
    model = Bookcase
    template_name = "books/bookcase_create.html"
    form_class = BookcaseCreateForm
    success_url = reverse_lazy("bookcase-list")


class BookcaseUpdateView(UpdateView):
    model = Bookcase
    template_name = "books/bookcase_update.html"
    fields = ["name", "description"]
    success_url = reverse_lazy("bookcase-list")
    queryset = Bookcase.objects.prefetch_related(
        Prefetch(
            "shelves",
            queryset=BookShelf.objects.annotate(
                book_count=Count("books"),
            ).select_related("bookcase"),
        ),
    )


class BookcaseDeleteView(DeleteView):
    model = Bookcase
    template_name = "books/bookcase_confirm_delete.html"
    success_url = reverse_lazy("bookcase-list")


class BookListView(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    paginate_by = 20


class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"


class BookCreateView(TemplateView):
    template_name = "books/book_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["isbn_form"] = AddByISBNForm()
        ctx["url_form"] = AddByURLForm()
        ctx["manual_form"] = ManualEntryForm()
        return ctx


class ManualEntryView(CreateView):
    model = Book
    form_class = ManualEntryForm
    template_name = "books/book_form.html#manual-section"
    success_url = reverse_lazy("book-list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["manual_form"] = ctx["form"]
        return ctx


class AddByURLView(CreateView):
    model = Book
    form_class = AddByURLForm
    template_name = "books/book_form.html#url-section"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("instance", None)
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["url_form"] = ctx["form"]
        return ctx

    def get_success_url(self):
        return f"/books/{self.object.pk}/"

    def form_valid(self, form):
        self.object = form.save()
        resp = self.render_to_response(self.get_context_data(form=form))
        resp["HX-Redirect"] = self.get_success_url()
        return resp


class AddByISBNView(CreateView):
    model = Book
    form_class = AddByISBNForm
    template_name = "books/book_form.html#isbn-section"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["isbn_form"] = ctx["form"]
        ctx["shelf"] = ctx["form"].cleaned_data.get("shelf")
        return ctx

    def get_success_url(self):
        return f"/books/{self.object.pk}/"

    def form_valid(self, form):
        resp = super().form_valid(form)
        resp["HX-Redirect"] = resp["Location"]
        del resp["Location"]
        return resp


class BookUpdateView(UpdateView):
    model = Book
    template_name = "books/book_form.html"
    fields = [
        "shelf",
        "title",
        "authors",
        "isbn",
        "publication_year",
    ]
    success_url = reverse_lazy("book-list")


class BookDeleteView(DeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy("book-list")


class ISBN(TemplateView):
    template_name = "isbn.html"

    def get_context_data(self, **kwargs):
        from app.metadata.services.base import get_book_by_isbn

        ctx = super().get_context_data(**kwargs)
        ctx["book"] = get_book_by_isbn(self.request.GET.get("isbn", ""))
        self.book = ctx["book"]
        return ctx

    def get(self, *args, **kwargs):
        resp = super().get(*args, **kwargs)
        if not self.book:
            resp.status_code = 400
        return resp


def autocomplete(request):
    mapping = {
        "bookcase": {
            "queryset": Bookcase.objects.prefetch_related(
                Prefetch(
                    "shelves",
                    queryset=BookShelf.objects.select_related("bookcase"),
                ),
            ),
            "filters": ["name__icontains"],
            "fields": ["id", "name", "shelves_config"],
        }
    }

    q = request.GET.get("q", "")
    model = request.GET.get("model", "")
    config = mapping.get(model)

    results = config["queryset"].filter(**{f: q for f in config["filters"]})

    return JsonResponse(
        {
            "results": [
                {field: getattr(result, field) for field in config["fields"]}
                for result in results
            ]
        }
    )

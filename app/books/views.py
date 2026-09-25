from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.views.decorators.csrf import csrf_exempt
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
from .models import (
    Author,
    Book,
    Bookcase,
    BookShelf,
)
from .permissions import PermissionMixin
from .utils import get_int_or_default


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["total_number_of_books"] = Book.objects.count()
        ctx["latest_books"] = Book.objects.order_by("-created_at")[:10]

        return ctx


class AuthorListView(PermissionMixin, ListView):
    model = Author
    queryset = Author.objects.all().order_by("name")
    template_name = "books/author/list.html"
    context_object_name = "authors"
    paginate_by = 20

    @cached_property
    def filter_data(self):
        return {
            "search": self.request.GET.get("search", "").strip(),
        }

    def get_queryset(self):
        authors = super().get_queryset()

        if search := self.filter_data["search"]:
            authors = authors.filter(name__icontains=search)

        return authors

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_data"] = self.filter_data
        return ctx


class AuthorDetailView(PermissionMixin, DetailView):
    model = Author
    template_name = "books/author/detail.html"


class AuthorCreateView(PermissionMixin, CreateView):
    model = Author
    template_name = "books/author/create.html"
    fields = ("name",)
    success_url = reverse_lazy("author-list")


class BookcaseListView(PermissionMixin, ListView):
    model = Bookcase
    queryset = Bookcase.objects.annotate(
        num_shelves=Count("shelves"),
        num_books=Count("shelves__books"),
    )
    template_name = "books/bookcase/list.html"
    context_object_name = "bookcases"


class BookcaseCreateView(PermissionMixin, CreateView):
    model = Bookcase
    template_name = "books/bookcase/create.html"
    form_class = BookcaseCreateForm
    success_url = reverse_lazy("bookcase-list")


class BookcaseDetailView(PermissionMixin, DetailView):
    model = Bookcase
    template_name = "books/bookcase/detail.html"
    queryset = Bookcase.objects.prefetch_related(
        Prefetch(
            "shelves",
            queryset=BookShelf.objects.annotate(
                book_count=Count("books"),
            ).select_related("bookcase"),
        ),
    )


class BookcaseUpdateView(PermissionMixin, UpdateView):
    model = Bookcase
    template_name = "books/bookcase/update.html"
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


class BookcaseDeleteView(PermissionMixin, DeleteView):
    model = Bookcase
    template_name = "books/bookcase/confirm_delete.html"
    success_url = reverse_lazy("bookcase-list")


class BookListView(PermissionMixin, ListView):
    model = Book
    queryset = Book.objects.order_by("-created_at")
    template_name = "books/book/list/index.html"
    context_object_name = "books"
    paginate_by = 20

    @cached_property
    def filter_data(self):
        return {
            "search": self.request.GET.get("search", "").strip(),
            "author": get_int_or_default(self.request.GET.get("author")),
            "bookcase": get_int_or_default(self.request.GET.get("bookcase")),
        }

    def get_queryset(self):
        books = super().get_queryset()

        if author_id := self.filter_data["author"]:
            books = books.filter(authors=author_id)

        if bookcase_id := self.filter_data["bookcase"]:
            books = books.filter(shelf__bookcase=bookcase_id)

        if search := self.filter_data["search"]:
            books = books.filter(Q(title__icontains=search) | Q(isbn=search))

        return books

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["view_modes"] = (
            ("cover", "photo"),
            ("table", "table"),
        )

        ctx["view_mode"] = {"table": "table"}.get(self.request.GET.get("view"), "cover")
        ctx["bookcases"] = Bookcase.objects.all().order_by("name")
        ctx["authors"] = Author.objects.all().order_by("name")
        ctx["filter_data"] = self.filter_data

        return ctx


class BookDetailView(PermissionMixin, DetailView):
    model = Book
    template_name = "books/book/detail.html"
    context_object_name = "book"


def get_initial_shelf(request):
    if shelf_id := request.session.get("last_used_shelf"):
        return BookShelf.objects.get(pk=shelf_id)


class BookCreateView(PermissionMixin, TemplateView):
    template_name = "books/book/create.html"
    model = Book  # required only for permission check

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        initial = {}
        if shelf := get_initial_shelf(self.request):
            initial["shelf"] = shelf
            ctx["shelf"] = shelf

        ctx["isbn_form"] = AddByISBNForm(initial=initial)
        ctx["url_form"] = AddByURLForm(initial=initial)
        ctx["manual_form"] = ManualEntryForm(initial=initial)

        return ctx


class CreateBookMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx[self.context_form_name] = ctx["form"]
        ctx["shelf"] = ctx["form"].cleaned_data.get("shelf")
        return ctx

    def get_success_url(self):
        return f"/books/{self.object.pk}/"

    def form_valid(self, form):
        resp = super().form_valid(form)
        resp["HX-Redirect"] = resp["Location"]

        if shelf := form.cleaned_data.get("shelf"):
            self.request.session["last_used_shelf"] = shelf.id

        del resp["Location"]
        return resp


class AddByISBNView(CreateBookMixin, PermissionMixin, CreateView):
    model = Book
    form_class = AddByISBNForm
    template_name = "books/book/create.html#isbn-section"
    context_form_name = "isbn_form"


class AddByURLView(CreateBookMixin, PermissionMixin, CreateView):
    model = Book
    form_class = AddByURLForm
    template_name = "books/book/create.html#url-section"
    context_form_name = "url_form"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # form_class is not a ModelForm
        kwargs.pop("instance", None)
        return kwargs


class ManualEntryView(CreateBookMixin, PermissionMixin, CreateView):
    model = Book
    form_class = ManualEntryForm
    template_name = "books/book/create.html#manual-section"
    success_url = reverse_lazy("book-list")
    context_form_name = "manual_form"


class BookUpdateView(PermissionMixin, UpdateView):
    model = Book
    template_name = "books/book/update.html"
    fields = [
        "shelf",
        "title",
        "authors",
        "isbn",
        "publication_year",
    ]
    success_url = reverse_lazy("book-list")


class BookDeleteView(PermissionMixin, DeleteView):
    model = Book
    template_name = "books/book/confirm_delete.html"
    success_url = reverse_lazy("book-list")


def autocomplete(request):
    if not request.user.is_authenticated:
        raise PermissionDenied

    # TOOD permission check based on selected mapping
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
        },
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


@csrf_exempt
@permission_required("books.add_book")
def add_by_isbn_api_view(request):
    if not request.user.is_authenticated:
        raise PermissionDenied

    form = AddByISBNForm(request.POST)
    if not form.is_valid():
        return JsonResponse(dict(form.errors), status=400)

    book = form.save()

    return JsonResponse({"success": True, "title": book.title}, status=200)

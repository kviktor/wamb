from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)

from app.users import forms
from app.users.models import User
from app.users.permissions import PermissionMixin


class LoginView(DjangoLoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("index")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_social_django_enabled"] = "social_django" in settings.INSTALLED_APPS
        return ctx


class UserListView(PermissionMixin, ListView):
    model = User
    template_name = "users/user/list.html"
    context_object_name = "users"


class UserCreateView(PermissionMixin, CreateView):
    model = User
    form_class = forms.UserCreateForm
    template_name = "users/user/create.html"

    def get_success_url(self):
        return reverse_lazy("user-list")


class UserDetailView(PermissionMixin, DetailView):
    model = User
    template_name = "users/user/update.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = ctx["user"]
        ctx["update_form"] = forms.UserUpdateForm(instance=user)
        ctx["password_form"] = SetPasswordForm(user=user)
        return ctx


class UserUpdateView(PermissionMixin, UpdateView):
    model = User
    template_name = "users/user/update.html#update-section"
    form_class = forms.UserUpdateForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["update_form"] = ctx["form"]
        return ctx

    def form_valid(self, form):
        self.object = form.save()
        return self.get(self.request, self.args, self.kwargs)


class SetPasswordView(PermissionMixin, UpdateView):
    model = User
    template_name = "users/user/update.html#password-section"
    form_class = SetPasswordForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["password_form"] = ctx["form"]
        return ctx

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = kwargs.pop("instance")
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return self.get(self.request, self.args, self.kwargs)

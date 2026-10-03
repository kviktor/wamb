from django.conf import settings
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy


class LoginView(DjangoLoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("index")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_social_django_enabled"] = "social_django" in settings.INSTALLED_APPS
        return ctx

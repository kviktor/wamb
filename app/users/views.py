from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy


class LoginView(DjangoLoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("index")

from django.urls import path

from app.users import views

urlpatterns = [
    # Bookcase URLs
    path("login/", views.LoginView.as_view(), name="login"),
]

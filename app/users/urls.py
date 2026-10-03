from django.urls import path

from app.users import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    # user management urls
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("users/new/", views.UserCreateView.as_view(), name="user-create"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/update/", views.UserUpdateView.as_view(), name="user-update"),
    path(
        "users/<int:pk>/set-password/",
        views.SetPasswordView.as_view(),
        name="user-set-password",
    ),
]

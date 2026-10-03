from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView,
)

from app.users.models import User


class PermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    check the base classes of the current CBV and guess the permission from that
    """

    def has_permission(self):
        if self.model is User:
            return self.request.user.can_manage_users

        for klass in self.__class__.__bases__:
            if klass in (CreateView, DeleteView, UpdateView):
                return self.request.user.can_change

        return self.request.user.can_view

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView,
)


class PermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    check the base classes of the current CBV and guess the permission from that
    """

    def get_permission_required(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name

        action = "view"
        for klass in self.__class__.__bases__:
            if klass is CreateView:
                action = "add"
                break
            elif klass is DeleteView:
                action = "delete"
                break
            elif klass is UpdateView:
                action = "change"
                break

        return (f"{app_label}.{action}_{model_name}",)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        ctx["permissions"] = {
            action: self.request.user.has_perm(f"{app_label}.{action}_{model_name}")
            for action in ("view", "change", "add", "delete")
        }
        return ctx

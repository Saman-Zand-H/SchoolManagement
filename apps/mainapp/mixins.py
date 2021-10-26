from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


class PermissionAndLoginRequiredMixin(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect("account_login")
        if not self.has_permission():
            raise PermissionDenied(self.get_permission_denied_message())
        return super().dispatch(request, *args, **kwargs)

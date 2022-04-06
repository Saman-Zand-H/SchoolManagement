from allauth.account.views import LogoutView

class CustomLogoutView(LogoutView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["segment"] = "logout"
        return context


logout_view = CustomLogoutView.as_view()

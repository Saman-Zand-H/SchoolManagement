from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from allauth.account.views import LogoutView, PasswordChangeView
from allauth.account.models import EmailAddress
from allauth.account.forms import ChangePasswordForm

from .forms import UserBioForm
from mainapp.models import Class, Student


class CustomLogoutView(LogoutView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["segment"] = "logout"
        return context


logout_view = CustomLogoutView.as_view()


class ProfileView(LoginRequiredMixin, View):
    template_name = "dashboard/profile.html"
    context = dict()

    def get(self, args, **kwargs):
        load_template = self.request.path.split()[-1]
        email_confirmed = EmailAddress.objects.filter(
            user=self.request.user).distinct()
        self.context.update({
            "form": ChangePasswordForm(),
            "segment": load_template,
            "nav_color": "bg-danger",
        })
        if email_confirmed.exists():
            self.context["email_confirmed"] = email_confirmed.first().verified
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        form = UserBioForm(self.request.POST)
        if form.is_valid():
            about = form.cleaned_data.get("about")
            self.request.user.about = about
            self.request.user.save()
            messages.success(self.request, _("Bio was updated successfully."))
            return redirect("profile")
        else:
            messages.error(self.request, _("Provided inputs are invalid."))
            self.context["form"] = form
            return render(self.request, self.template_name, self.context)


profile_view = ProfileView.as_view()


class CustomPasswordChangeView(LoginRequiredMixin,
                               PasswordChangeView):
    permission_required = "supports.support"
    template_name = "dashboard/profile.html"
    success_url = reverse_lazy("profile")

    def render_to_response(self, context, **response_kwargs):
        classes = Class.objects.filter(school__support=self.request.user)
        students = Student.objects.filter(student_class__in=classes).distinct()
        context["classes_count"] = classes.count()
        context["students_count"] = students.count()

        if not self.request.user.has_usable_password():
            return redirect("profile")
        return super().render_to_response(context, **response_kwargs)
    
    
custom_password_change_view = CustomPasswordChangeView.as_view()

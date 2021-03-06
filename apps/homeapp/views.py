from functools import partial
from django.views.generic import TemplateView, View
from django.utils.translation import activate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

import logging
from typing import Any, Dict
from smtplib import SMTPException

from mainapp.models import School, Article, Assignment
from mainapp.mixins import PermissionAndLoginRequiredMixin
from .forms import SupportForm, ArticleForm, AssignmentForm, OperationType
from .tasks import support_email_task
from supports.forms import EditOperationType

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_anonymous:
            context["school"] = School.objects.filter(
                support=self.request.user)
        return context


homepageview = HomePageView.as_view()


class SupportView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "dashboard/support.html", {
            "form": SupportForm(),
            "segment": "support-page",
            "nav_color": "bg-gradient-purple",
        })

    def post(self, *args, **kwargs):
        form = SupportForm(self.request.POST)
        logger.info(
            f"{self.request.user} tried to send a support message.")

        if form.is_valid():
            user_name = form.cleaned_data.get("name")
            user_email = form.cleaned_data.get("email")
            user_message = form.cleaned_data.get("text")
            try:
                support_email_task.delay(user_name, 
                                         user_email, 
                                         user_message)
            except SMTPException as e:
                logger.error(
                    f"There was an error while user {self.request.user} "
                    "was trying to send a support message! The problem "
                    "caused by the email API.")
                logger.error(f"Error: {e}")
                messages.error(
                    self.request,
                    "An internal error happened. Please call us as soon as you can."
                )
            return redirect("home:support-page")
        else:
            messages.error(self.request, "Provided inputs are invalid.")
            return render(self.request, "dashboard/support.html",
                          {"form": form})


support_view = SupportView.as_view()


def set_language(request):
    if request.method == "POST":
        user_language = request.POST.get("language")
        activate(user_language)
        response = HttpResponseRedirect(reverse("home:home"))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
        return response

    return redirect("home:home")


class ArticlesTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/articles/articles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        school = self.request.user.school
        context["articles"] = Article.objects.filter(school=school)
        context["segment"] = self.request.path.split("/")
        context["nav_color"] = "bg-gradient-info"
        return context


articles_template_view = ArticlesTemplateView.as_view()


class AddArticleView(LoginRequiredMixin, View):
    template_name = "dashboard/articles/add_article.html"
    context = dict()

    def get(self, *args, **kwargs):
        self.context.update({
            "segment": self.request.path.split("/"),
            "form": ArticleForm(),
            "nav_color": "bg-gradient-danger",
        })
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        form = ArticleForm(self.request.POST)
        school = get_object_or_404(School, support=self.request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = self.request.user
            article.save()
            messages.success(self.request,
                             "Article saved successfully.")
            return redirect("home:article-detail", pk=article.pk)
        else:
            messages.error(self.request, "Provided inputs are invalid.")
        return redirect("home:articles")


add_article_view = AddArticleView.as_view()


class ArticleDetailView(LoginRequiredMixin, View):
    template_name = "dashboard/articles/article_detail.html"
    context = dict()

    def get(self, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs["pk"])
        self.context.update({
            "article": article,
            "form": ArticleForm(instance=article),
            "segment": self.request.path.split("/"),
            "nav_color": "bg-gradient-info",
        })
        return render(self.request, self.template_name, self.context)

    def post(self, *args, **kwargs):
        operation_form = EditOperationType(self.request.POST)
        if operation_form.is_valid():
            operation = operation_form.cleaned_data.get("operation")
            match operation:
                case "da":
                    article = get_object_or_404(Article, pk=kwargs["pk"])
                    if (
                        article.author == self.request.user
                        or (
                            self.author.school_name == self.request.user.school_name
                            and self.request.user.has_perm("supports:support")
                        )
                    ):
                        article.delete()
                        messages.success(
                            self.request, "Article deleted successfully.")
                        return redirect("home:articles")
                    raise PermissionDenied()


article_detail_view = ArticleDetailView.as_view()


class AssignmentsView(LoginRequiredMixin, View):
    template_name = "dashboard/assignments/assignments.html"
    context = dict()
    
    def get(self, *args, **kwargs):
        assignment_instances = Assignment.objects.none()
        match self.request.user.user_type:
            case "SS" | "T":
                assignment_instances = Assignment.objects.filter(
                    assignment_class__school=self.request.user.school).distinct()
            case "S":
                assignment_instances = Assignment.objects.filter(
                    assignment_class=self.request.user.student.user.student_class
                )
        self.context.update({
            "nav_color": "bg-gradient-indigo",
            "assignments": assignment_instances.order_by("-deadline"),
            "segment": self.request.path.split("/"),
        })
        return render(self.request, self.template_name, self.context)


assignments_view = AssignmentsView.as_view()


class AddAssignmentView(PermissionAndLoginRequiredMixin, View):
    permission_required = "teachers.teacher"
    template_name = "dashboard/assignments/add_assignment.html"
    context = dict()
    
    def get(self, *args, **kwargs):
        self.context.update({
            "nav_color": "bg-gradient-indigo",
            "form": AssignmentForm(request=self.request),
            "segment": self.request.path.split("/"),
        })
        return render(self.request, self.template_name, self.context)
    
    def post(self, *args, **kwargs):
        form = AssignmentForm(data=self.request.POST, request=self.request)
        if form.is_valid():
            instance = form.save()
            messages.success(self.request, "Assignment saved successfully.")
            return redirect(instance.get_absolute_url())
        messages.error(self.request, "Provided inputs are invalid.")
        self.context.update({"form": form})
        return render(self.request, self.template_name, self.context)
            


add_assignment_view = AddAssignmentView.as_view()


class AssignmentDetailView(LoginRequiredMixin, View):
    template_name = "dashboard/assignments/assignments_detail.html"
    context = dict()
    
    def get(self, *args, **kwargs):
        assignment = get_object_or_404(Assignment, pk=kwargs["pk"])
        self.context.update({
            "assignment": assignment.reversed(),
            "form": AssignmentForm(request=self.request, instance=assignment),
            "nav_color": "bg-gradient-indigo",
            "segment": self.request.path.split("/"),
        })
        return render(self.request, self.template_name, self.context)
    
    def post(self, *args, **kwargs):
        operation_form = OperationType(self.request.POST)
        success_message = partial(messages.success, request=self.request)
        error_message = partial(messages.error, request=self.request)
        if operation_form.is_valid():
            operation = operation_form.cleaned_data.get("operation")
            match operation:
                case "ea":
                    assignment = get_object_or_404(Assignment, pk=kwargs["pk"])
                    if assignment.subject.teacher.user == self.request.user:
                        a_form = AssignmentForm(
                            request=self.request, data=self.request.POST, instance=assignment)
                        if a_form.is_valid():
                            a_form.save()
                            success_message(message="Assignment updated successfully.")
                            return redirect(assignment.get_absolute_url())
                        error_message(message="Provided inputs are invalid.")
                        self.context.update({"form": a_form})
                        return render(self.request, self.template_name, self.context)
                    raise PermissionDenied("You are not the teacher of this assignment.")
    
    
assignment_detail_view = AssignmentDetailView.as_view()


class GuideTemplateView(TemplateView):
    template_name = "dashboard/guide.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "segment": self.request.path.split("/"),
            "nav_color": "bg-gradient-orange",
        })
        return context


guide_template_view = GuideTemplateView.as_view()

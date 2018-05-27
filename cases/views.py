from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.views.generic.edit import FormMixin
from .models import Person, Case
from .forms import CaseUpdateForm, IntakeForm


# Caseworker login page
class OfficeLoginView(LoginView):
    template_name = 'cases/login.html'


# Used for logout button, simply redirects to login page
def logout_view(request):
    logout(request)
    return redirect(settings.LOGIN_REDIRECT_URL)


# Information on all of one caseworker's cases
class CaseListView(LoginRequiredMixin, generic.DetailView):
    model = Person
    template_name = 'cases/caselist.html'


# Overview of all the information and updates for a single case
class CaseDetailView(LoginRequiredMixin, FormMixin, generic.DetailView):
    model = Case
    template_name = 'cases/casedetail.html'
    form_class = CaseUpdateForm

    def get_success_url(self):
        return reverse('cases:case_detail', args=(self.object.pk,))

    def get_context_data(self, **kwargs):
        context = super(CaseDetailView, self).get_context_data(**kwargs)
        context['form'] = CaseUpdateForm(initial={'case': self.object})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super(CaseDetailView, self).form_valid(form)


class CaseOpenCloseView(LoginRequiredMixin, generic.edit.UpdateView):
    model = Case
    fields = []
    template_name = 'cases/caseopenclose.html'

    def form_valid(self, form):
        if self.object.close_date:  # Reopening a case
            self.object.close_date = None
        else:  # Closing a case
            self.object.close_date = timezone.now()
        self.object.isOpen = not self.object.isOpen
        self.object.save()
        return redirect('/')


# Case intake form
class IntakeView(LoginRequiredMixin, generic.FormView):
    template_name = 'cases/intake.html'
    form_class = IntakeForm
    success_url = '/'  # Go to homepage

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@login_required
def home_view(request):
    return redirect(reverse('cases:case_list', args=(request.user.caseworker.slug,)))

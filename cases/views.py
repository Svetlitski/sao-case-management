from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
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

# Information on all of one caseworker's cases, viewable only by them
class CaseListView(LoginRequiredMixin, generic.DetailView):
    model = Person
    template_name = 'cases/caselist.html'


class CaseDetailView(LoginRequiredMixin, FormMixin, generic.DetailView):
    model = Case
    template_name = 'cases/casedetail.html'
    form_class = CaseUpdateForm
    success_url = '/'  # TODO: figure out how to replace this with a call to reverse

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


# Case intake form
class IntakeView(LoginRequiredMixin, generic.FormView):
    template_name = 'cases/intake.html'
    form_class = IntakeForm
    success_url = '/'  # Go to homepage

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


# Home page reached after login
class HomeView(LoginRequiredMixin, generic.ListView):
    template_name = 'cases/home.html'
    context_object_name = 'caseworker'

    def get_queryset(self):
        return Person.objects.get(account=self.request.user)

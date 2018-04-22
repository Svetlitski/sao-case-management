from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings

from .models import Person, IntakeForm, Case


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


# For recording case updates
class CaseUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Case
    fields = ['incident_description', 'isOpen', 'close_date']
    template_name = 'cases/caseupdate.html'


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

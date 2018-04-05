from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect

from .models import Person, IntakeForm


# Caseworker login page
class OfficeLoginView(LoginView):
    template_name = 'cases/login.html'
    next = '/home'


def logout_view(request):
    logout(request)
    return redirect('login/')


# List of all caseworkers, serving as a directory of sorts
class IndexView(LoginRequiredMixin, generic.ListView):
    login_url = 'login/'
    template_name = 'cases/index.html'
    context_object_name = 'caseworker_list'

    def get_queryset(self):
        return Person.objects.order_by('name')


# Information on all of a caseworker's cases
class PersonDetailView(LoginRequiredMixin, generic.DetailView):
    login_url = 'login/'
    model = Person
    template_name = 'cases/persondetail.html'


# Intake form
class IntakeView(LoginRequiredMixin, generic.FormView):
    login_url = 'login/'
    template_name = 'cases/intake.html'
    form_class = IntakeForm
    success_url = '/'  # Go to homepage

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


# Homepage reached after login
class HomeView(IndexView):
    template_name = 'cases/home.html'

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView


from .models import Person, IntakeForm


class OfficeLoginView(LoginView):
    template_name = 'cases/login.html'
    next = '/home'


class IndexView(LoginRequiredMixin, generic.ListView):
    login_url = 'login/'
    template_name = 'cases/index.html'
    context_object_name = 'caseworker_list'

    def get_queryset(self):
        return Person.objects.order_by('name')


class PersonDetailView(LoginRequiredMixin, generic.DetailView):
    login_url = 'login/'
    model = Person
    template_name = 'cases/persondetail.html'


class IntakeView(LoginRequiredMixin, generic.FormView):
    login_url = 'login/'
    template_name = 'cases/intake.html'
    form_class = IntakeForm
    success_url = '/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class HomeView(IndexView):
    template_name = 'cases/home.html'

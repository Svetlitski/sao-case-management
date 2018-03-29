from django.views import generic
from django.urls import resolve

from .models import Person, IntakeForm


class IndexView(generic.ListView):
    template_name = 'cases/index.html'
    context_object_name = 'caseworker_list'

    def get_queryset(self):
        return Person.objects.order_by('name')


class PersonDetailView(generic.DetailView):
    model = Person
    template_name = 'cases/persondetail.html'


class IntakeView(generic.FormView):
    template_name = 'cases/intake.html'
    form_class = IntakeForm
    success_url = '/'
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class HomeView(IndexView):
    template_name = 'cases/home.html'

#from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils import timezone

from .models import Case, Person


class IndexView(generic.ListView):
    template_name = 'cases/index.html'
    context_object_name = 'caseworker_list'

    def get_queryset(self):
        return Person.objects.order_by('name')

class PersonDetailView(generic.DetailView):
    model = Person
    template_name = 'cases/persondetail.html'

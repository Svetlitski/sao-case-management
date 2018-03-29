from django.shortcuts import render, get_object_or_404
from django.views import generic

class IndexView(generic.ListView):
	template_name = 'cases/index.html'
	context_object_name = 'open_cases_list'


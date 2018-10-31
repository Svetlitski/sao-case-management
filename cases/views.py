from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic.edit import FormMixin
from django.conf import settings

from .models import Case
from .forms import CaseUpdateForm, IntakeForm


# Information on all of one caseworker's cases
class CaseListView(LoginRequiredMixin, generic.ListView):
    model = Case
    template_name = 'cases/caselist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case_list'] = self.request.user.caseworker.case_set.all()
        return context


# Overview of all the information and updates for a single case
class CaseDetailView(LoginRequiredMixin, FormMixin, generic.DetailView):
    model = Case
    template_name = 'cases/casedetail.html'
    form_class = CaseUpdateForm

    def get_success_url(self):
        return reverse('cases:case_detail', args=(self.object.pk,))

    def get_context_data(self, **kwargs):
        context = super(CaseDetailView, self).get_context_data(**kwargs)
        context['form'] = CaseUpdateForm(initial={'case': self.object, 'creator': self.request.user.caseworker})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.caseworker in self.object.caseworkers.all():
            return super(CaseDetailView, self).get(request, *args, **kwargs)
        else:
            return redirect(reverse('home'))

    def form_valid(self, form):
        form.save()
        return super(CaseDetailView, self).form_valid(form)


class CaseOpenCloseView(LoginRequiredMixin, generic.edit.UpdateView):
    model = Case
    fields = []
    template_name = 'cases/caseopenclose.html'

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        if self.object.is_open:  # Closing a case
            self.object.close_date = timezone.now()
        else:  # Reopening a case
            self.object.close_date = None
        self.object.is_open = not self.object.is_open
        self.object.save()
        return super().form_valid(form)


# Case intake form
class IntakeView(LoginRequiredMixin, generic.FormView):
    template_name = 'cases/intake.html'
    form_class = IntakeForm

    def get_success_url(self):
        return reverse('home')

    def get_initial(self):
        initial = super(IntakeView, self).get_initial()
        initial['intake_caseworker'] = self.request.user.caseworker
        return initial

    def form_valid(self, form):
        case = form.save()
        if not settings.LOCAL:
            form.send_notification_email(case.id)
        return super().form_valid(form)

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic.edit import FormMixin
from django.conf import settings

from .models import Case
from .forms import CaseUpdateForm, IntakeForm


class UserAssignedToCaseMixin(UserPassesTestMixin):
    """
    Responds with 403 Forbidden if a user attempts to access a case
    which they are not assigned to.
    """ 
    def test_func(self):
        self.object = self.get_object()
        return self.request.user.caseworker in self.object.caseworkers.all()


class CaseListView(LoginRequiredMixin, generic.ListView):
    """
    Displays all the cases assigned to a user, serving as a homepage.
    """ 
    model = Case
    template_name = 'cases/caselist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case_list'] = self.request.user.caseworker.case_set.all()
        return context


class CaseDetailView(LoginRequiredMixin, UserAssignedToCaseMixin, FormMixin, generic.DetailView):
    """
    Displays detailed information on a single case including: the client's name and contact
    information, the case intake description and the name of the intake caseworker,
    and all updates associated with the case. If the case is closed the close date is also shown.
    A case is also managed through this view, updates are added from this view and the 
    CaseChange and CaseOpenClose views for a case are linked from here.
    """
    model = Case
    template_name = 'cases/casedetail.html'
    form_class = CaseUpdateForm

    def get_success_url(self):
        return reverse('cases:case_detail', args=(self.object.pk,))

    def get_context_data(self, **kwargs):
        context = super(CaseDetailView, self).get_context_data(**kwargs)
        # case and creator fields on case update are not shown to the user, but are instead filled in automatically here
        context['form'] = CaseUpdateForm(initial={'case': self.object, 'creator': self.request.user.caseworker})
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


class CaseChangeView(LoginRequiredMixin, UserAssignedToCaseMixin, generic.UpdateView):
    """
    Allows a user to add/update information about the client of an existing case.
    """
    model = Case
    template_name = 'cases/casechange.html'
    fields = ['client_name', 'client_phone', 'client_email', 'client_SID']
    

    def get_success_url(self):
        return reverse('cases:case_detail', args=(self.object.pk,))


class CaseOpenCloseView(LoginRequiredMixin, UserAssignedToCaseMixin, generic.edit.UpdateView):
    """
    Simple view allowing a user to close or reopen a case.
    """
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


class IntakeView(LoginRequiredMixin, generic.FormView):
    """
    Allows a user to fill out an intake, creating a new case.
    """
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

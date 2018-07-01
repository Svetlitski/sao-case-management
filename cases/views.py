from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic.edit import FormMixin
import sendgrid
import os
from sendgrid.helpers.mail import *
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
        context['form'] = CaseUpdateForm(initial={'case': self.object})
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

    def form_valid(self, form):
        if self.object.is_open:  # Closing a case
            self.object.close_date = timezone.now()
        else:  # Reopening a case
            self.object.close_date = None
        self.object.is_open = not self.object.is_open
        self.object.save()
        return redirect(reverse('home'))


# Case intake form
class IntakeView(LoginRequiredMixin, generic.FormView):
    template_name = 'cases/intake.html'
    form_class = IntakeForm

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        """
        TODO: Make this work without having to hardcode emails in
        """
        new_case = form.save()
        # Now send a notification email
        sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])
        from_email = Email('notifications@saoberkeley.herokuapp.com')
        advocate_email = Email("advocate@berkeleysao.org")
        subject = 'A new case has been opened'
        object_url = reverse('admin:cases_case_change', kwargs={'object_id': new_case.id})
        content = Content("text/html", "<html><body><p> A new case has been added, <a href=%s> click here</a> to view it.</p></body></html>" % object_url)
        notification_mail = Mail(from_email, subject, advocate_email, content)
        #personalization = notification_mail.personalizations[0]
        #additional_recipients = ['saochief@asuc.org', 'chief@berkeleysao.org']
        #for division in new_case.divisions:
        sg.client.mail.send.post(request_body=notification_mail.get())
        return super().form_valid(form)

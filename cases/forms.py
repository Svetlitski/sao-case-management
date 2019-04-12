from django.forms import ModelForm
from django import forms
from .models import Case, CaseUpdate, Tag
from django.contrib.auth.models import Group
from django.urls import reverse
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
import sendgrid
import os
from sendgrid.helpers.mail import *
from tinymce import TinyMCE
from django.contrib.admin.widgets import AutocompleteSelect, AutocompleteSelectMultiple
from django.contrib.admin import site as admin_site

TINY_MCE_SETUP = {'browser_spellcheck': True, 'valid_elements': 'a,strong,p,ul,ol,li,em,h1,h2,h3', 'valid_children': '-li[p]',
                  'toolbar': ['formatselect | bold italic | bullist numlist link'], 'statusbar': False,
                  'block_formats': 'Paragraph=p;Heading 1=h1;Heading 2=h2;Heading 3=h3',
                  'plugins': 'paste, link, lists'
                  }


class CaseUpdateForm(ModelForm):
    class Meta:
        model = CaseUpdate
        fields = ['update_description', 'case', 'creator']
        labels = {'update_description': ""}
        # user does not manually select which case a case update is for, or the creator
        widgets = {'case': forms.HiddenInput(), 'creator': forms.HiddenInput(), 'update_description': TinyMCE(mce_attrs={'height': 200, **TINY_MCE_SETUP})}

    def save(self, commit=True):
        case_update = super().save()
        case_update.case.last_updated = case_update.creation_date
        case_update.case.save()
        case_update.save()
        return case_update


class CaseChangeForm(ModelForm):
    class Meta:
        model = Case
        fields = ['client_name', 'client_phone', 'client_email', 'client_SID', 'referrer', 'tags']
        widgets = {
               'referrer': AutocompleteSelect(rel=Tag.cases.rel, admin_site=admin_site),
               'tags': AutocompleteSelectMultiple(rel=Case.tags.rel, admin_site=admin_site),
                  }

    def clean(self):
        cleaned_data = super().clean()
        tags = cleaned_data['tags']
        case_divisons = self.instance.divisions
        for tag in tags:
            for div in tag.divisions:
                if div in case_divisons:
                    break
            else:
                raise forms.ValidationError("Invalid tag for case of this division")


class IntakeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.keys():
            """
            Having the user's web browser autocomplete any of the fields
            on the intake form makes no sense, so we prevent it from occurring.
            """
            self.fields[field].widget.attrs.update(autocomplete='off')
        self.fields['incident_description'].required = False  # Neccessary for validation on other fields to work properly

    class Meta:
        model = Case
        fields = ['divisions', 'client_name',
                  'client_email', 'client_phone', 'client_SID', 'open_date',
                  'incident_description', 'intake_caseworker', 'referrer']
        widgets = {'client_phone': PhoneNumberInternationalFallbackWidget(),
                   'incident_description': TinyMCE(mce_attrs=TINY_MCE_SETUP),
                   'intake_caseworker': forms.HiddenInput(),
                   'referrer': AutocompleteSelect(rel=Tag.cases.rel, admin_site=admin_site),
                   }

    def build_notification_email(self, object_id):
        """
        Builds a notification email addressed to the internal chief, advocate,
        and relevant division leads informing them that a new case has been created 
        upon submission of the IntakeForm.
        """
        notification_mail = Mail()
        notification_mail.from_email = Email(
            'notifications@saoberkeley.herokuapp.com')
        notification_mail.subject = 'A new case has been opened: %s, %s' % (
            self.cleaned_data['client_name'], self.cleaned_data['divisions'])
        object_url = 'https://saoberkeley.herokuapp.com' + reverse('admin:cases_case_change',
                             kwargs={'object_id': object_id})
        notification_mail.add_content(Content(
            "text/html", "<html><body><p> A new case has been opened, <a href=%s> click here</a> to view it.</p></body></html>" % object_url))
        personalization = Personalization()
        for user in Group.objects.get(name='Intake Recipients').user_set.all():  # Internal chief and advocate, at least at the time this was written
            personalization.add_to(Email(user.email))
        for user in Group.objects.get(name='Division Leads').user_set.all():
            if user.caseworker.division in self.cleaned_data['divisions']:
                personalization.add_to(Email(user.email))
        notification_mail.add_personalization(personalization)
        return notification_mail.get()

    def send_notification_email(self, object_id):
        sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])
        data = self.build_notification_email(object_id)
        sg.client.mail.send.post(request_body=data)

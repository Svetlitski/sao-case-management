from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from django.utils.html import format_html


ACADEMIC = 'ACA'
GRIEVANCE = 'GRI'
FIN_AID = 'FIN'
CONDUCT = 'CON'
DIVISION_CHOICES = (
    (ACADEMIC, 'Academic'),
    (GRIEVANCE, 'Grievance'),
    (FIN_AID, 'Financial Aid'),
    (CONDUCT, 'Conduct')
)


# An individual caseworker
class Person(models.Model):
    name = models.CharField(max_length=30)
    division = models.CharField(
        max_length=3,
        choices=DIVISION_CHOICES,
        default=ACADEMIC,
    )
    account = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name='caseworker')

    def __str__(self):
        num_open = self.number_of_active_cases
        return self.name + ": " + str(num_open) + (" open case" if num_open == 1 else " open cases")

    @property
    def number_of_active_cases(self):
        return self.case_set.filter(is_open=True).count()

    class Meta:
        verbose_name = 'Caseworker'
        ordering = ['name']


class Case(models.Model):
    client_name = models.CharField(max_length=30)
    client_email = models.EmailField(blank=True)
    client_phone = PhoneNumberField(blank=True)
    client_SID = models.CharField(max_length=10, blank=True)
    incident_description = models.TextField()
    open_date = models.DateField('date case was opened', auto_now_add=True)
    close_date = models.DateField(
        'date case was closed', blank=True, null=True)
    caseworkers = models.ManyToManyField(Person, blank=True)
    divisions = MultiSelectField(choices=DIVISION_CHOICES)
    is_open = models.BooleanField('case open?', default=True)
    last_updated = models.DateTimeField(
        'time since last update', auto_now_add=True)

    def __str__(self):
        return self.client_name + ", " + str(self.open_date) + ", " + str(self.divisions)

    def clean(self):
        if(not (self.client_email or self.client_phone)):
            raise ValidationError(
                "You must record the client's contact information.")

    def updates(self):
        updates_information = ""
        for update in self.caseupdate_set.all():
            # Using format_html instead of string substitution in loop in order to sanitize input
            updates_information += format_html('<p> <b> {} </b> – {} </p>',
                                               update.creation_date.strftime("%B %d, %Y at %X"), update.update_description)
        return format_html(updates_information)

    def display_client_phone(self):
        phone_string = str(self.client_phone)
        formatted_phone_string_without_country_code = phone_string[2:5] + \
            '-' + phone_string[5:8] + '-' + phone_string[8:]
        if phone_string[0:2] == '+1':  # if this is a US phone number
            return formatted_phone_string_without_country_code
        else:
            return phone_string[0:2] + '-' + formatted_phone_string_without_country_code

    class Meta:
        ordering = ['-last_updated']  # ordered by most recent


class CaseUpdate(models.Model):
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_description = models.TextField()

    def __str__(self):
        return self.creation_date.strftime("%B %d, %Y at %X") + ' – ' + str(self.update_description)

    class Meta:
        ordering = ['-creation_date']  # ordered by most recent

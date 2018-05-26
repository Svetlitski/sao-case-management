from django.db import models
from django.utils.text import slugify
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
    division = models.CharField(
        max_length=3,
        choices=DIVISION_CHOICES,
        default=ACADEMIC,
    )
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30, default="")  # slug is based on name
    account = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name='caseworker')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.account:
            myUser = User.objects.create_user(
                self.name, self.name + "@berkeleysao.org", "default")
            myUser.save()
            self.account = myUser
        super().save()

    def __str__(self):
        num_open = self.number_of_active_cases
        return self.name + ": " + str(num_open) + (" open case" if num_open == 1 else " open cases")

    @property
    def number_of_active_cases(self):
        return len(self.case_set.filter(isOpen=True))

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
    isOpen = models.BooleanField('case open?', default=True)
    slug = models.SlugField(max_length=30, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # TODO: come up with a better slug that will still be unique
            self.slug = slugify(self.pk)
        super().save()

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
        client_phone_string = str(self.client_phone)
        return client_phone_string[0:2] + '-' + client_phone_string[2:5] + '-' + client_phone_string[5:8] + '-' + client_phone_string[8:]

    @property
    def last_updated(self):
        update_set = self.caseupdate_set.all()
        return update_set[0].creation_date if update_set else self.open_date


class CaseUpdate(models.Model):
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_description = models.TextField()

    def __str__(self):
        return self.creation_date.strftime("%B %d, %Y at %X") + ' – ' + str(self.update_description)

    class Meta:
        ordering = ['-creation_date']  # ordered by most recent

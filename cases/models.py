from django.db import models
from django.forms import ModelForm
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
import datetime


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


class Person(models.Model):
    division = models.CharField(
        max_length=3,
        choices=DIVISION_CHOICES,
        default=ACADEMIC,
    )
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30, default="")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save()

    def __str__(self):
        return self.name


year_from_now = datetime.date.today()
year_from_now = datetime.date(
    year_from_now.year + 1, year_from_now.month, year_from_now.day)


class Case(models.Model):
    client_name = models.CharField(max_length=30)
    client_email = models.EmailField(default="")
    client_phone = PhoneNumberField(default="")
    client_SID = models.CharField(max_length=10, default="")
    incident_description = models.TextField(default="")
    open_date = models.DateField('Date case was opened', auto_now_add=True)
    close_date = models.DateField('Date case was closed', default=year_from_now)
    caseworker = models.ForeignKey(
        Person, on_delete=models.CASCADE, default=None)
    division = models.CharField(
        max_length=3, choices=DIVISION_CHOICES, default=ACADEMIC)
    isOpen = models.BooleanField(default=True)

    def get_division(self):
        return self.caseworker.get_division_display()

    def __str__(self):
        return self.client_name + ", " + self.open_date.__str__() + ", " + self.get_division()


class IntakeForm(ModelForm):
    class Meta:
        model = Case
        fields = ('client_name', 'incident_description',
                  'caseworker')
        widgets = {'datetime'}

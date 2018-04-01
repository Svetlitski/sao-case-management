from django.db import models
from django.forms import ModelForm
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User


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
    slug = models.SlugField(max_length=30, default="")
    account = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True)

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
        return self.name

    def number_of_active_cases(self):
        return len(self.case_set.filter(isOpen=True))

    class Meta:
        verbose_name = 'Caseworker'


class Case(models.Model):
    client_name = models.CharField(max_length=30)
    client_email = models.EmailField(default="")
    client_phone = PhoneNumberField(default="")
    client_SID = models.CharField(max_length=10, default="")
    incident_description = models.TextField(default="")
    open_date = models.DateField('date case was opened', auto_now_add=True)
    close_date = models.DateField(
        'date case was closed', default=None, blank=True, null=True)
    caseworker = models.ForeignKey(
        Person, on_delete=models.CASCADE, default=None, blank=True, null=True)
    division = models.CharField(
        max_length=3, choices=DIVISION_CHOICES, default=ACADEMIC)
    isOpen = models.BooleanField('case open?', default=True)

    def __str__(self):
        return self.client_name + ", " + self.open_date.__str__() + ", " + self.division


class IntakeForm(ModelForm):
    class Meta:
        model = Case
        fields = ['division', 'client_name',
                  'client_email', 'client_phone', 'client_SID',
                  'incident_description']

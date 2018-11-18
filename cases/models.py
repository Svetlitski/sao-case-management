from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils import timezone
from tinymce import HTMLField


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


def get_current_date():
    """
    Used as default for open_date on Case.
    Not defined as a lambda because Django can't serialize lambdas.
    """
    return timezone.localdate(timezone.now())



class Person(models.Model):
    """
    Represents an individual caseworker. Akin to a User's profile. This class would be better
    named 'Caseworker', but because the system is now in production and changing the name would
    require modifying the tables in the database, it's been left as is.

    :instance_attribute name: The caseworker's full name (i.e. first and last, separated by a space)
    :instance_attribute division: The division the caseworker is a part of (for executive leadership this should
    be assigned to the division they used to be a part of).
    :instance_attribute account: The User associated with this caseworker
    """
    name = models.CharField(max_length=30)
    division = models.CharField(
        max_length=3,
        choices=DIVISION_CHOICES,
        default=ACADEMIC,
    )
    account = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name='caseworker')

    def __str__(self):
        num_open = self.number_of_open_cases
        return self.name + ": " + str(num_open) + (" open case" if num_open == 1 else " open cases")

    @property
    def number_of_open_cases(self):
        return self.case_set.filter(is_open=True).count()

    class Meta:
        verbose_name = 'Caseworker'
        ordering = ['name']


class Case(models.Model):
    """
    A case – an individual's grievance with the university plus the members of the office who are assisting them.
    
    :instance_attribute client_name: The client's full name (i.e. first and last, separated by a space)
    :instance_attribute client_email: The client's email address
    :instance_attribute client_phone: The client's phone number
    :instance_attribute client_SID: The client's UC Berkeley Student Identification number
    :instance_attribute incident_description: A summary of the client's situation/grievance, recorded by the intake caseworker
    :instance_attribute open_date: The date this case was opened, usually the day the intake was submitted
    :instance_attribute close_date: The date the case was closed. Note that if a case is reopened this information is lost
    :instance_attribute intake_caseworker: The caseworker who submitted the intake which created this case
    :instance_attribute caseworkers: The caseworker(s) assigned to this case
    :instance_attribute divisions: Which of the four divisions this case falls under
    :instance_attribute is_open: Whether or not this case is still open (i.e. being actively worked on)
    :instance_attribute last_updated: The last time a case update was made for this case
    """
    client_name = models.CharField(max_length=30)
    client_email = models.EmailField(blank=True)
    client_phone = PhoneNumberField(blank=True)
    client_SID = models.CharField(max_length=10, blank=True)
    incident_description = HTMLField()
    open_date = models.DateField('date case was opened', default=get_current_date)
    close_date = models.DateField(
        'date case was closed', blank=True, null=True)
    intake_caseworker = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='intakes')
    caseworkers = models.ManyToManyField(Person, blank=True)
    divisions = MultiSelectField(choices=DIVISION_CHOICES)
    is_open = models.BooleanField('case open?', default=True)
    last_updated = models.DateTimeField(
        'time since last update', auto_now_add=True)

    def __str__(self):
        return self.client_name + ", " + str(self.open_date) + ", " + str(self.divisions)

    def clean(self):
        """
        When a case is submitted *some* contact information must be recorded in the system,
        otherwise there is no way to follow up with the client!
        """
        if(not (self.client_email or self.client_phone)):
            raise ValidationError(
                "You must record the client's contact information.")

    def updates(self):
        """
        Returns a html escaped string which contains all of the information associated with
        the case updates which have been made for this case, all nicely formatted for display
        on the admin site.
        """
        if self.caseworkers.count() > 1:
            update_descriptions = (((update.creation_date.strftime("%B %d, %Y at %I:%M %p"), '[' + update.creator.name + ']'if update.creator is not None else '', mark_safe(update.update_description)) for update in self.caseupdate_set.all()))
        else:
            update_descriptions = (((update.creation_date.strftime("%B %d, %Y at %I:%M %p"), '', mark_safe(update.update_description)) for update in self.caseupdate_set.all()))
        return format_html_join('', "<p> <b> {} {}</b></p> {} ", update_descriptions)

    def display_client_phone(self):
        """
        Formats the client's phone number for display, removing the country code
        if the number is a US number.
        """
        phone_string = str(self.client_phone)
        formatted_phone_string_without_country_code = phone_string[2:5] + \
            '-' + phone_string[5:8] + '-' + phone_string[8:]
        if phone_string[0:2] == '+1':  # if this is a US phone number
            return formatted_phone_string_without_country_code
        else:
            return phone_string[0:2] + '-' + formatted_phone_string_without_country_code

    @property
    def client_initials(self):
        """ 
        Used in the CaseList view to allow a user to identify a case
        without the client's name or personal information being displayed.
        """
        return '.'.join([name[0] for name in self.client_name.split()])

    class Meta:
        ordering = ['-last_updated']  # ordered by most recent


class CaseUpdate(models.Model):
    """
    A case update, created to record progress made and new information learned
    during the course of a case

    :instance_attribute case: The case this update is about
    :instance_attribute creation_date: The date and time this update was created
    :instance_attribute update_description: The information this update is recording
    :instance_attribute creator: The caseworker who created this update (useful when multiple people are assigned to a case)
    """
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_description = HTMLField()
    creator = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.creation_date.strftime("%B %d, %Y at %X") + ' – ' + str(self.update_description)

    class Meta:
        ordering = ['-creation_date']  # ordered by most recent

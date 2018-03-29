from django.db import models
#from django.utils.text import slugify


class Person(models.Model):
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
    division = models.CharField(
        max_length=3,
        choices=DIVISION_CHOICES,
        default=ACADEMIC,
    )
    name = models.CharField(max_length=30)
    """
    slug = models.SlugField(max_length=30)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save()
    """

    def __str__(self):
        return self.name


class Case(models.Model):
    case_short_description = models.CharField(max_length=200)
    open_date = models.DateTimeField('date case was opened')
    caseworker = models.ForeignKey(Person, on_delete=models.CASCADE, default=None)
    isOpen = models.BooleanField(default=True)

    def __str__(self):
        return self.case_short_description

# Create your models here.

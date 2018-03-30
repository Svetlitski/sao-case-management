from django.contrib import admin
admin.AdminSite.site_header = "SAO Case Administration"

from .models import Case, Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    fields = ['name', 'division']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    fields = ['client_name', 'caseworker',
              'incident_description', 'open_date', 'isOpen']
    list_display = ('get_division', 'caseworker',
                    'open_date', 'client_name', 'isOpen')
    list_filter = ['open_date', 'isOpen']
    search_fields = ['incident_description']

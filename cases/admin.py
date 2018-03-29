from django.contrib import admin

from .models import Case, Person


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    fields = ['client_name', 'caseworker',
              'case_short_description', 'open_date', 'isOpen']
    list_display = ('get_division', 'caseworker',
                    'open_date', 'client_name', 'isOpen')
    list_filter = ['open_date', 'isOpen']
    search_fields = ['case_short_description']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    fields = ['name', 'division']

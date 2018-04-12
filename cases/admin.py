from .models import Case, Person

from django.contrib import admin
admin.AdminSite.site_header = "SAO Case Administration"


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    fields = ['name', 'division']
    list_display = ('name', 'division', 'number_of_active_cases')
    list_filter = ['division']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    fields = ['divisions', 'caseworkers', 'client_name',
              'client_email', 'client_phone', 'client_SID',
              'incident_description', 'isOpen', 'close_date']
    list_display = ('get_divisions_display',
                    'open_date', 'client_name', 'isOpen')
    list_filter = ['open_date', 'isOpen', 'divisions']
    search_fields = ['incident_description']

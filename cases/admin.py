from .models import Case, Person, DIVISION_CHOICES
from django.contrib import admin
admin.AdminSite.site_header = "SAO Case Administration"


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    fields = ['name', 'division']
    list_display = ('name', 'division', 'number_of_active_cases')
    list_filter = ['division']
    search_fields = ['name']


class DivisionsListFilter(admin.SimpleListFilter):
    title = 'division'
    parameter_name = 'division'

    def lookups(self, request, model_admin):
        return DIVISION_CHOICES

    def queryset(self, request, queryset):
        if(self.value() is None):
            return queryset
        return queryset.filter(divisions__contains=self.value())


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    fields = ['divisions', 'caseworkers', 'client_name',
              'client_email', 'client_phone', 'client_SID',
              'incident_description', 'is_open', 'close_date', 'updates']
    readonly_fields = ['updates']
    list_display = ('get_divisions_display',
                    'open_date', 'client_name', 'is_open')
    list_filter = ['open_date', 'is_open', DivisionsListFilter]
    search_fields = ['incident_description']
    autocomplete_fields = ['caseworkers']

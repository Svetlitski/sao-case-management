from .models import Case, Person, DIVISION_CHOICES
from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils import timezone

admin.AdminSite.site_header = "SAO Case Administration"


class CasesInline(admin.TabularInline):
    model = Case.caseworkers.through
    extra = 0
    verbose_name = 'case'
    verbose_name_plural = 'cases'


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    fields = ['name', 'division', 'account']
    list_display = ('name', 'division', 'number_of_active_cases')
    list_filter = ['division']
    search_fields = ['name']
    inlines = [CasesInline]


class DivisionsListFilter(admin.SimpleListFilter):
    title = 'division'
    parameter_name = 'division'

    def lookups(self, request, model_admin):
        return DIVISION_CHOICES

    def queryset(self, request, queryset):
        if(self.value() is None):
            return queryset
        return queryset.filter(divisions__contains=self.value())


def close_cases(modeladmin, request, queryset):
    queryset.update(is_open=False, close_date=timezone.now())


def reopen_cases(modeladmin, request, queryset):
    queryset.update(is_open=True, close_date=None)


close_cases.short_description = "Close selected cases"
reopen_cases.short_description = "Reopen selected cases"


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    fields = ['divisions', 'caseworkers', 'client_name',
              'client_email', 'client_phone', 'client_SID', 'open_date',
              'incident_description', 'is_open', 'close_date', 'updates']
    readonly_fields = ['updates']
    list_display = ('get_divisions_display',
                    'open_date', 'client_name', 'is_open')
    list_filter = ['open_date', 'is_open', DivisionsListFilter]
    search_fields = ['incident_description']
    autocomplete_fields = ['caseworkers']
    actions = [close_cases, reopen_cases]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user in Group.objects.get(name='Office Leads').user_set.all():
            return qs  # Chiefs and advocate can see everything
        return qs.filter(divisions__contains=request.user.caseworker.division)

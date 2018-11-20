from .models import Case, Person, Tag, DIVISION_CHOICES
from django.contrib import admin
from tinymce import HTMLField, TinyMCE
from django.contrib.auth.models import Group
from django.utils import timezone
from cases.forms import TINY_MCE_SETUP
admin.AdminSite.site_header = "SAO Case Administration"


class CasesInline(admin.TabularInline):
    model = Case.caseworkers.through
    extra = 0
    verbose_name = 'case'
    verbose_name_plural = 'cases'
    template = 'admin/tabular.html'


    def get_queryset(self, request):
        """
        Filters case queryset so that executive leadership (users in 'Office Leads')
        can see all cases associated with a caseworker, but division leads can only see
        the cases which fall under their division
        """
        qs = super().get_queryset(request)
        if request.user in Group.objects.get(name='Office Leads').user_set.all():
            return qs  # Chiefs and advocate can see everything
        return qs.filter(case__divisions__contains=request.user.caseworker.division)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filters case queryset so that executive leadership (users in 'Office Leads')
        can see all cases associated with a caseworker, but division leads can only see
        the cases which fall under their division
        """
        if db_field.name == 'case' and request.user not in Group.objects.get(name='Office Leads').user_set.all():
            kwargs["queryset"] = Case.objects.filter(divisions__contains=request.user.caseworker.division)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    fields = ['name', 'division', 'account']
    list_display = ('name', 'division', 'number_of_open_cases')
    list_filter = ['division']
    search_fields = ['name']
    inlines = [CasesInline]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if request.user in Group.objects.get(name='Office Leads').user_set.all():
            extra_context['case_statuses'] = [case_caseworkers.case.is_open for case_caseworkers in Case.caseworkers.through.objects.filter(person_id=object_id)]
        else:
            extra_context['case_statuses'] = [case_caseworkers.case.is_open for case_caseworkers in Case.caseworkers.through.objects.filter(person_id=object_id).filter(case__divisions__contains=request.user.caseworker.division)]
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

class DivisionsListFilter(admin.SimpleListFilter):
    """
    A custom list filter to filter objects by division.
    Neccessary because django-multiselect-field package is used
    with division on Case objects, and the MultiSelectField
    provided by it is not automatically supported by the django admin.
    """
    title = 'division'
    parameter_name = 'division'

    def lookups(self, request, model_admin):
        return DIVISION_CHOICES

    def queryset(self, request, queryset):
        if(self.value() is None):
            return queryset
        return queryset.filter(divisions__contains=self.value())


def close_cases(modeladmin, request, queryset):
    """
    Closes selected cases and records the current date as the cases' close date.
    """
    queryset.update(is_open=False, close_date=timezone.now())


def reopen_cases(modeladmin, request, queryset):
    """
    Reopens selected cases and removes their close dates.
    """
    queryset.update(is_open=True, close_date=None)


close_cases.short_description = "Close selected cases"
reopen_cases.short_description = "Reopen selected cases"


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    fields = ['divisions', 'caseworkers', 'intake_caseworker', 'referrer', 'client_name',
              'client_email', 'client_phone', 'client_SID', 'open_date', 'incident_description',
              'tags', 'is_open', 'close_date', 'updates']
    readonly_fields = ['updates', 'intake_caseworker']
    list_display = ('get_divisions_display',
                    'open_date', 'client_name', 'is_open')
    list_filter = ['open_date', 'is_open', DivisionsListFilter]
    search_fields = ['incident_description', 'client_name']
    autocomplete_fields = ['caseworkers', 'tags']
    actions = [close_cases, reopen_cases]
    formfield_overrides = {HTMLField: {'widget': TinyMCE(mce_attrs={'width': '75%', **TINY_MCE_SETUP})}}

    def get_queryset(self, request):
        """
        Filters case queryset so that executive leadership (users in 'Office Leads')
        can see all cases in the system, but division leads can only see
        the cases which fall under their division
        """
        qs = super().get_queryset(request)
        if request.user in Group.objects.get(name='Office Leads').user_set.all():
            return qs  # Chiefs and advocate can see everything
        return qs.filter(divisions__contains=request.user.caseworker.division)

    def save_model(self, request, obj, form, change):
        if change:
            was_open_before_change = Case.objects.get(pk=obj.pk).is_open
            if (not obj.is_open) and was_open_before_change and (not obj.close_date):
                # If the case was just closed but the user did not input a close date, set the close date to today.
                obj.close_date = timezone.now()
            elif obj.is_open and (not was_open_before_change):
                # If the case was just reopened, set the close date to None
                obj.close_date = None
        else:
            if (not obj.is_open) and (not obj.close_date):
                # If a new case was just created but is closed (i.e. consultation) and the user did not select a close date, set the close date to today
                obj.close_date = timezone.now()
        obj.save()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ['value', 'acronym']
    search_fields = ['value', 'acronym']

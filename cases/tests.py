from django.test import TestCase, Client
import factory
import factory.fuzzy
import random
from .models import Person, Case, CaseUpdate, DIVISION_CHOICES
from django.contrib.auth.models import User, Group
from collections import defaultdict
from django.conf import settings
from django.core import management
import phonenumbers
DIVISION_DATABASE_VALUES = [pair[0] for pair in DIVISION_CHOICES]
import re



def close_date_fuzzer():
    if random.randint(0, 1):
        return factory.Faker('future_date', end_date="+180d").generate({})
    else:
        return None


def divisions_fuzzer():
    return set(random.choices(DIVISION_DATABASE_VALUES, k=random.randrange(1, 5)))

non_number = re.compile('[^\d]+')
def phone_number_fuzzer():
    phone_number = phonenumbers.parse('9999999999', 'US') # deliberately invalid
    while not phonenumbers.is_valid_number(phone_number):
        try:
            phone_number = phonenumbers.parse(non_number.sub('', factory.Faker('phone_number').generate({})), 'US')
        except NumberParseException:
            pass
    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.NATIONAL)
    




class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = 'user'
    password = 'supersecretfake' # not used for anything


class PersonFactory(factory.DjangoModelFactory):
    class Meta:
        model = Person

    name = factory.Faker('name')
    division = factory.fuzzy.FuzzyChoice(DIVISION_DATABASE_VALUES)
    account = factory.SubFactory(
        UserFactory, username=factory.LazyAttribute(lambda o: o.factory_parent.name.lower().replace(' ', '-')))


class CaseUpdateFactory(factory.DjangoModelFactory):
    class Meta:
        model = CaseUpdate
    case = None
    creation_date = factory.LazyAttribute(lambda o: factory.Faker('date_time_between_dates', datetime_start=o.case.open_date, datetime_end=(
        None if not o.case.close_date else o.case.close_date)).generate({}))
    update_description = factory.Faker('paragraph')

    @factory.post_generation
    def creator(self, create, extracted, **kwargs):
        if extracted:
            self.creator = extracted
        elif self.case and self.case.caseworkers.count() > 0:
            self.creator = random.choice(self.case.caseworkers.all())


class CaseFactory(factory.DjangoModelFactory):
    class Meta:
        model = Case

    client_name = factory.Faker('name')
    client_email = factory.LazyAttribute(
        lambda o: ('%s@berkeley.edu' % o.client_name).lower().replace(' ', '-'))
    client_phone = factory.fuzzy.FuzzyAttribute(fuzzer=phone_number_fuzzer)
    client_SID = factory.Faker('isbn10', separator="")
    incident_description = factory.LazyFunction(lambda: '<p>' + factory.Faker('paragraph').generate({}) + '</p>')
    open_date = factory.Faker('past_date', start_date="-1y")
    close_date = factory.Maybe('is_open', yes_declaration=None,
                               no_declaration=factory.Faker('future_date', end_date="+180d"))
    divisions = factory.fuzzy.FuzzyAttribute(fuzzer=divisions_fuzzer)
    is_open = factory.fuzzy.FuzzyAttribute(
        fuzzer=lambda: bool(random.randint(0, 1)))

    @factory.post_generation
    def caseworkers(self, create, extracted, **kwargs):
        if extracted:
            caseworkers_by_division = defaultdict(lambda: [])
            for caseworker in extracted:
                caseworkers_by_division[caseworker.division].append(caseworker)
            for div in self.divisions:
                self.caseworkers.add(random.choice(caseworkers_by_division[div]))
        else:
            self.caseworkers.set([PersonFactory.create(
                division=div) for div in self.divisions])

    @factory.post_generation
    def intake_caseworker(self, create, extracted, **kwargs):
        if extracted:
            self.intake_caseworker = random.choice(extracted)

    @factory.post_generation
    def case_update_set(self, create, extracted, **kwargs):
        self.caseupdate_set.set(CaseUpdateFactory.create_batch(
            random.randint(1, 5), case=self))


class CaseModelTest(TestCase):
    @classmethod
    def setUpTestData(self):
        # First make sure we create at least one caseworker for each division
        self.caseworkers = [PersonFactory.create(
            division=div) for div in DIVISION_DATABASE_VALUES]
        # Then create more caseworkers randomly for a total of 50
        self.caseworkers += PersonFactory.create_batch(46)
        self.cases = CaseFactory.create_batch(
            200, caseworkers=self.caseworkers)

    def test_case_closed_or_open_matches_date(self):
        for case in self.cases:
            if case.is_open:
                self.assertEqual(case.close_date, None)
            else:
                self.assertNotEqual(case.close_date, None)

    def test_contact_information_present(self):
        for case in self.cases:
            self.assertTrue(case.client_phone or case.client_email)

    def test_caseworkers_assigned_by_division(self):
        for case in self.cases:
            for caseworker in case.caseworkers.all():
                self.assertTrue(caseworker.division in case.divisions)


class CaseCloseOpenTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.caseworkers = [PersonFactory.create(
            division=div) for div in DIVISION_DATABASE_VALUES]
        for caseworker in self.caseworkers:
            caseworker.case_set.add(CaseFactory.create(caseworkers={caseworker.division: [
                                    caseworker]}, divisions=[caseworker.division], is_open=True))
            caseworker.case_set.add(CaseFactory.create(caseworkers={caseworker.division: [
                                    caseworker]}, divisions=[caseworker.division], is_open=False))

    def test_close_case(self):
        caseworker = self.caseworkers[0]
        number_open_cases = caseworker.number_of_open_cases
        open_case = caseworker.case_set.get(is_open=True)
        open_case.is_open = False
        open_case.save()
        self.assertEqual(caseworker.number_of_open_cases,
                         number_open_cases - 1)

    def test_open_case(self):
        caseworker = self.caseworkers[0]
        number_open_cases = caseworker.number_of_open_cases
        closed_case = caseworker.case_set.get(is_open=False)
        closed_case.is_open = True
        closed_case.save()
        self.assertEqual(caseworker.number_of_open_cases,
                         number_open_cases + 1)


def create_office(num_caseworkers=50, num_cases=200):
    """
    Flushes the database and then populates it with test data and creates a demo account.
    Used to set things up locally for testing and demonstrations.
    """
    if not settings.LOCAL:
        print("You can't run this in production! Aborting.")
        return
    valid_input = False
    while not valid_input:
        proceed = input('This will delete all existing information in the local database. Are you sure you want to continue ([y]/n)? ')
        if proceed == 'n':
            return
        elif proceed == '' or proceed == 'y':
            valid_input = True
    print('PLEASE CONFIRM YOU ARE 100% SURE OF WHAT YOU ARE DOING')
    management.call_command('flush', interactive=True)
    print("Demo account created with username 'demo'. Please enter a password.")
    management.call_command('createsuperuser', username='demo', email='demo@berkeleysao.org')
    demo_caseworker = PersonFactory.create(name='Demo Caseworker', division='ACA', account=User.objects.get(username='demo'))
    caseworkers = [PersonFactory.create(division=div) for div in DIVISION_DATABASE_VALUES] + PersonFactory.create_batch(num_caseworkers - 5) + [demo_caseworker]
    CaseFactory.create_batch(num_cases, caseworkers=caseworkers, intake_caseworker=caseworkers)
    if demo_caseworker.number_of_open_cases < 3:
        num_cases += (3 - demo_caseworker.number_of_open_cases)
        CaseFactory.create_batch(3 - demo_caseworker.number_of_open_cases, caseworkers=[demo_caseworker], divisions=['ACA'], intake_caseworker=caseworkers)
    Group.objects.create(name='Office Leads')
    Group.objects.create(name='Division Leads')
    print('Office successfully created with %d caseworkers and %d cases.' % (num_caseworkers, num_cases))
    




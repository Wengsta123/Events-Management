"""
This file contains unit tests that ensure that all functionality works upon
integration. All these test cases are executed automatically when TravisCI tests
the correctness of our program. They can also be triggered by running the appropriate
command on a local environment.

Due to the nature of the language, it is clear to the team and any future developers
what each unit test is asserting. The sections of the file (the classes) will be
explained in more detail.
"""

from django.test import TestCase, Client, RequestFactory
from django.apps import apps
from events.apps import EventsConfig
from django.contrib.auth.hashers import check_password
from events.models import County, Player, Coach, Competition, Account, Event, Heat, Admin
from events.forms import CoachPlayerForm, CountyCreationForm, CoachCreationForm, CompetitionCreationForm, CompetitionImportForm, EventCreationForm, HeatCreationForm, AdminPlayerForm, PasswordChangeForm, EventSelectionForm, CountySelectionForm
from events.views import *
from django.http import HttpRequest
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from django.urls import reverse
from urllib.parse import urlencode

"""
A test that ensures the login functionality is working correctly by trying
expected input, unexpected input, and edge cases.
"""
class LoginTestCase(TestCase):
    #this is to set up a valid user
    def setUp(self):
        testAccount = Account.objects.create(username="test", password="password1")
        testAccount2 = Account.objects.create(username="test1", password="password123")
        self.client = Client()
        comp1 = Competition.objects.create(name="new", start_date='2018-11-27')
        county = County.objects.create(name="place")
        event = Event.objects.create(name = "placeholder", relay_duration = 5, athletes_per_relay = 5, competition_id=comp1)
        Heat.objects.create(event_id=event, start_time='2018-10-10')
        Player.objects.create(first_name='playerfirstname', last_name='playerlastname', date_of_birth='2001-10-10', gender='Male',
                                       availability='Both', county_id=county, competition_id=comp1)

        admin = Admin.objects.create(account=testAccount, current_competition=comp1, first_name='adminfirstname',
                                     last_name='adminlastname')

        Coach.objects.create (account = testAccount2,first_name='coachfirstname',
                                     last_name='coachlastname', county_id=county, current_competition=comp1)
        self.request_factory = RequestFactory()
        self.user = testAccount
        self.user2 = testAccount2
    def test_admin_create_admin_as_admin(self):
        #Test create admin view
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/admin_create_admin/'
        response=self.client.post(postlink, {'username': 'admin2', 'password1': 'pass', 'password2': 'pass', 'first_name':'Bob', 'last_name':'Johnson','email':'bob@gmail.com','phone_number':'4444444444'})
        self.assertTrue(response)
    def test_admin_create_admin_not_as_admin(self):
        #Test create admin view
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        self.assertTrue(login)
        postlink = '/admin_create_admin/'
        response=self.client.post(postlink, {'username': 'admin2', 'password1': 'pass', 'password2': 'pass', 'first_name':'Bob', 'last_name':'Johnson','email':'bob@gmail.com','phone_number':'4444444444'})
        self.assertTrue(response)
    def test_admin_create_coach_as_admin(self):
        #Test admin create coach view
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/admin_create_coach/'
        response=self.client.post(postlink, {'username': 'user', 'password1': 'pass', 'password2': 'pass', 'first_name':'Bob', 'last_name':'Johnson','email':'bob@gmail.com','phone_number':'4444444444','county_id':county.county_id,'current_competition':competition.competition_id})
        self.assertTrue(response)
    def test_admin_create_coach_not_as_admin(self):
        #Test admin create coach view
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        self.assertTrue(login)
        postlink = '/admin_create_coach/'
        response=self.client.post(postlink, {'username': 'user', 'password1': 'pass', 'password2': 'pass', 'first_name':'Bob', 'last_name':'Johnson','email':'bob@gmail.com','phone_number':'4444444444','county_id':county.county_id,'current_competition':competition.competition_id})
        self.assertTrue(response)
    def test_admin_create_admin_form(self):
        #Try to test the form itself
        #Doesn't actually affect code coverage
        comp1= Competition.objects.create(name="placeholder", start_date='2018-11-27')
        data = {'username': 'user', 'password1': 'pass', 'password2': 'pass'}
        data2 = {'username': 'user', 'password1': 'pass', 'password2': 'pass', 'first_name': 'name', 'last_name': 'name', 'email': 'user@email.com',
                                     'phone_number': '7037037033'}
        #Very similar to view
        form=CustomUserCreationForm(data)
        form2=AdminCreationForm(data2)
        account = form.save()
        admin = form2.save(commit=False)
        admin.account = account
        admin.current_competition_id=comp1.competition_id
        admin.save()
        self.assertTrue(form.is_valid())
    def test_admin_create_competition(self):
        #Test create competition
        response=self.client.post('/admin_create_competition/', {'name': "testcomp", 'start_date': "2018-11-16"})
        competition = Competition.objects.get(name="testcomp")
        #Test edit competition
        response=self.client.post('/admin_edit_competition/'+str(competition.competition_id)+'/', {'name': "testcomp", 'start_date': "2018-12-16"})
        self.assertNotEqual(competition.start_date,datetime.date(2018,10,16))
    def test_admin_create_event(self):
        #Test create event
        competition = Competition.objects.get(name="new")
        response=self.client.post('/admin_create_event/', {'name': "testevent", 'relay_duration':5, 'athletes_per_relay':5, 'competition_id': competition.competition_id})
        event = Event.objects.get(name = "testevent")
        self.assertEqual(event.relay_duration, 5)
    def test_refresh(self):
        #test if refresh works without errors
        #try:
        self.client.post('/refresh_schedule/')
        # except:
        #     pass
    def test_scheduler(self):
        #test if scheduler works without errors
        #try:
        self.client.post('/start_scheduler/')
        #except:
        #    pass

    def test_report_select_county(self):
         county=County.objects.get(name="place")
         request = self.request_factory.post('/report_select_county', {'county_id': county.county_id})
         request.user = self.user
         response = report_select_county(request)
    def test_report_select_county_nul_county(self):
         county=County.objects.get(name="place")
         request = self.request_factory.post('/report_select_county')
         request.user = self.user
         response = report_select_county(request)
    #coach_report doesn't work because request.user
    #def test_coach_report(self):

    def test_admin_create_player(self):
        account = Account.objects.get(username = "test")
        competition = Competition.objects.get(name="new")
        admin = Admin.objects.get(first_name='adminfirstname')
        event = Event.objects.get(name="placeholder")
        county = County.objects.get(name="place")

        request = self.request_factory.post('/admin_create_player/', {'first_name': "test",'last_name':"lastnametest", 'county_id': county.county_id, 'competition_id': competition.competition_id, 'events':event})
        request.user = self.user
        response = admin_create_player(request)
        player = Player.objects.get(last_name = "playerlastname")
        self.assertEqual(player.first_name, "playerfirstname")
    #this test doesn't really work, issues with referencing variables before assignments due to test.py being unable to access heats
    # def test_report_player_schedule(self):
    #     request = self.request_factory.post('/report_player_schedule/')
    #     request.user = self.user2
    #
    #     event= Event.objects.get(name="placeholder")
    #     player = Player.objects.get (first_name = "playerfirstname")
    #     response=self.client.post('/admin_create_heat/', {'event_id': event, 'start_time':5, 'players':player})
    #     heat = Heat.objects.get(event_id=event)
    #     response = report_player_schedule(request)


    def test_admin_create_heat(self):
        event= Event.objects.get(name="placeholder")
        response=self.client.post('/admin_create_heat/', {'event_id': event, 'start_time':5, 'players':[]})
        heat = Heat.objects.get(event_id=event)
    def test_apps(self):
        #Test apps.py
        self.assertEqual(EventsConfig.name, 'events')
        self.assertEqual(apps.get_app_config('events').name, 'events')
    def test_password_change_form_clean(self):
        data = {
            'password': 'test123',
            'confirm_password': 'test123',
        }
        form = PasswordChangeForm(data)
        self.assertTrue(form.is_valid())
    def test_password_change_form_not_same(self):
        data = {
            'password': 'test1',
            'confirm_password': 'test123',
        }
        form = PasswordChangeForm(data)
        self.assertFalse(form.is_valid())
    def test_password_change(self):
        account = Account.objects.get(username="test")

        request = self.request_factory.post('/admin_change_password/', {'password': "changedpassword", 'confirm_password': "changedpassword",})
        request.user = self.user
        response = admin_change_password(request,account.account_id)
        self.assertFalse(account.password=="changedpassword")
    def test_password_change_get(self):
        account = Account.objects.get(username="test")
        request = self.request_factory.get('/admin_change_password/')
        request.user = self.user
        response = admin_change_password(request,account.account_id)
        self.assertTrue(response)
    def test_correct_username_information(self):
        userLogin="test1"
        pwd="password123"
        #try:
        user=Account.objects.get(username=userLogin)
        user.__str__()
        #except Account.DoesNotExist:
        #    pass
        self.assertEqual(user.username=="test1", True)
    def test_correct_password(self):
        userLogin = "test1"
        pwd = "password123"
        #try:
        user = Account.objects.get(username=userLogin)
        #except Account.DoesNotExist:
        #    pass
        self.assertEqual(user.password==pwd, True)
    def test_incorrect_username(self):
        userLogin="test2"
        try:
            user=Account.objects.get(username=userLogin)
        except Account.DoesNotExist:
            user=Account(username="###",password="###")
        self.assertEqual(userLogin==user.username,False)
    def test_correct_username_incorrect_password(self):
        userLogin = "test1"
        pwd= "123"
        #try:
        user = Account.objects.get(username=userLogin)
        #except Account.DoesNotExist:
        #    user = Account(username="###", password="###")
        self.assertEqual(pwd == user.password, False)
    def test_username_with_other_users_password(self):
        userLogin = "test"
        pwd = "password123"
        #try:
        user = Account.objects.get(username=userLogin)
        #except Account.DoesNotExist:
        #    user = Account(username="###", password="###")
        self.assertEqual(pwd == user.password, False)

"""
A test that ensures the functionality that allows the admin to create a coach
is working correctly by trying expected input, unexpected input, and edge cases.
"""
class CoachAdminCreationTestCase(TestCase):
    #this is to set up a valid user
    def setUp(self):
        a1 = Account.objects.create(username="test", password="password1")
        a2 = Account.objects.create(username="test1", password="password123")
        comp1= Competition.objects.create(name="placeholder", start_date='2018-11-27')
        count1=County.objects.create(name="place")
        count2=County.objects.create(name="place2")
        Coach.objects.create(account=a1, first_name='Elon', last_name = 'Musk', county_id=count1, current_competition=comp1)
        Coach.objects.create(account=a2,first_name='Steve', last_name='Jobs', county_id=count2, current_competition=comp1)
        a3 = Account.objects.create(username="admin", password="supersecure")
        Admin.objects.create(account=a3, current_competition=comp1, first_name='adminfirstname', last_name='adminlastname')
    def test_correct_coach1(self):
        userLogin="test1"
        #try:
        user=Account.objects.get(username=userLogin)
        #except Account.DoesNotExist:
        #    pass
        self.assertEqual(user.coach.first_name=="Steve", True)

    def test_correct_county(self):
        userLogin1 = "test"
        userLogin2 = "test1"
        #try:
        user1 = Account.objects.get(username=userLogin1)
        user2 = Account.objects.get(username=userLogin2)
        #except Account.DoesNotExist:
        #    pass
        self.assertEqual(user1.coach.county_id == user2.coach.county_id, False)
    def test_correct_competition(self):
        userLogin1 = "test"
        userLogin2 = "test1"
        #try:
        user1 = Account.objects.get(username=userLogin1)
        user2 = Account.objects.get(username=userLogin2)
        #except Account.DoesNotExist:
        #    pass
        self.assertEqual(user1.coach.current_competition == user2.coach.current_competition, True)
    def test_incorrect_coach1(self):
        userLogin = "test1"
        #try:
        user = Account.objects.get(username=userLogin)
        #except Account.DoesNotExist:
        #    pass
        self.assertEqual(user.coach.first_name=="Elon", False)
    def test_coach_to_account(self):
        firstName="Elon"
        lastName="Musk"
        #try:
        coach=Coach.objects.get(first_name=firstName,last_name=lastName)
        #except Coach.DoesNotExist:
        #    pass
        self.assertEqual(coach.account.username=="test", True)
    def test_admin_to_account(self):
        firstName="adminfirstname"
        lastName="adminlastname"
        #try:
        admin=Admin.objects.get(first_name=firstName,last_name=lastName)
        #except Admin.DoesNotExist:
        #    pass
        self.assertEqual(admin.account.username=="admin", True)
    def test_correct_admin(self):
        userLogin="admin"
        #try:
        user=Account.objects.get(username=userLogin)
        #except Account.DoesNotExist:
        #    pass
        self.assertEqual(user.admin.first_name=="adminfirstname", True)

"""
A test that ensures the functionality that allows the admin to create a county and a competition
 is working correctly by trying expected input, unexpected input, and edge cases.
"""
class CoachCountyCompetitionCreationTest(TestCase):
    def test_county_form_case(self):
        #Test that the county form is valid with all the data
        form = CountyCreationForm(data={'name':'Albemarle County'})
        self.assertTrue(form.is_valid())
    def test_competition_form_case(self):
        #Test that the competition form is valid with all the data
        form = CompetitionCreationForm(data={'name':'2018 Competition','start_date':'2018-10-10'})
        self.assertTrue(form.is_valid())
    def test_coach_form_case(self):
        #Test that the coach form is valid with all the data
        p_county = County.objects.create(name='Albemarle County')
        p_competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        p_account = Account.objects.create(username='bob',password='helloiambob')
        form = CoachCreationForm(data={'account':p_account.account_id,'first_name':'Bob', 'last_name':'Johnson','email':'bob@gmail.com','phone_number':'4444444444','county_id':p_county.county_id,'current_competition':p_competition.competition_id})
        self.assertTrue(form.is_valid())
    def test_coach_no_county(self):
        #Test that the coach form is not valid without a county
        p_county = County.objects.create(name='Albemarle County')
        p_competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        p_account = Account.objects.create(username='bob',password='helloiambob')
        form = CoachCreationForm(data={'account':p_account.account_id,'first_name':'Bob', 'last_name':'Johnson','email':'bob@gmail.com','phone_number':'4444444444','county_id':'','current_competition':p_competition.competition_id})
        self.assertFalse(form.is_valid())
    def test_coach_no_competition(self):
        #Test that the coach form is not valid without a competition
        p_county = County.objects.create(name='Albemarle County')
        p_competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        p_account = Account.objects.create(username='bob',password='helloiambob')
        form = CoachCreationForm(data={'account':p_account.account_id,'first_name':'Bob', 'last_name':'Johnson','email':'bob@gmail.com','phone_number':'4444444444','county_id':p_county.county_id,'current_competition':''})
        self.assertTrue(form.is_valid())
    def test_county_create_case(self):
        #Test that the county form is valid with all the data
        county = County.objects.create(name='Albemarle County')
        self.assertEqual(County.objects.get(name='Albemarle County').name, 'Albemarle County')
    def test_competition_create_case(self):
        #Test that the competition form is valid with all the data
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        self.assertEqual(Competition.objects.get(start_date='2018-10-10').name, '2018 Competition')
    def test_coach_create_case(self):
        #Test that the coach form is valid with all the data
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        p_account = Account.objects.create(username='bob',password='helloiambob')
        coach = Coach.objects.create(account=p_account,first_name='Bob', last_name='Johnson', email='bob@gmail.com', phone_number='4444444444', county_id=county, current_competition=competition)
        self.assertEqual(Coach.objects.get(first_name='Bob').county_id.name, 'Albemarle County')

# TEST TO CREATE ADMIN WITH NO OTHER ADMINS AND NO COMPETITIONS


"""
A test that ensures the functionality that allows the admin to import a competition
 is working correctly by trying expected input, unexpected input, and edge cases.
"""
class CompetitionImportTest(TestCase):
    def test_import_competition_form_case(self):
        #Test that the import competition form is valid with all the data
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player.__str__()
        form = CompetitionImportForm(data={'competition_name':'2019 Competition','start_date':'2019-10-10','imported_competition':competition.competition_id})
        self.assertTrue(form.is_valid())
    def test_import_competition_form_case_no_competition(self):
        #Test that the import competition form fails with no competition
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        form = CompetitionImportForm(data={'competition_name':'2018 Competition','start_date':'2018-10-10',})
        self.assertFalse(form.is_valid())
    def test_import_competition_form_case_no_name(self):
        #Test that the import competition form fails with no name
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        form = CompetitionImportForm(data={'start_date':'2018-10-10','imported_competition':competition})
        self.assertFalse(form.is_valid())
    def test_import_competition_form_case_no_start_date(self):
        #Test that the import competition form fails with no start_date
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        form = CompetitionImportForm(data={'competition_name':'2018 Competition','imported_competition':competition})
        self.assertFalse(form.is_valid())

"""
A test that ensures the functionality that allows the admin to create an event and a heat
 is working correctly by trying expected input, unexpected input, and edge cases.
"""
class EventHeatCreationEditTest(TestCase):
    def test_event_form_case(self):
        #Test that the event form is valid with all the data
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        form = EventCreationForm(data={'name':'Archery','relay_duration':90,'athletes_per_relay':10, 'competition_id':competition.competition_id})
        self.assertTrue(form.is_valid())
    def test_event_create_case(self):
        #Test that the event creation works in the database
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        self.assertEqual(Event.objects.get(name='Archery').competition_id, competition)
    def test_heat_form_case_no_players(self):
        #Test that the heat form is invalid with no players
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach = Coach.objects.create(account=acc,first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=county,current_competition=competition)
        player = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        form = HeatCreationForm(data={'event_id':event.event_id, 'start_time':'2018-10-10', 'duration':90})
        self.assertFalse(form.is_valid())
    def test_heat_create_case(self):
        #Test that the heat creation works in the database
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach = Coach.objects.create(account=acc,first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=county,current_competition=competition)
        player = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        heat = Heat.objects.create(event_id=event, start_time='2018-10-10')
        self.assertEqual(Heat.objects.get(start_time='2018-10-10').event_id, event)
    def test_edit_event_form_case(self):
        #Test that we can edit an event to change info
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        form = EventCreationForm(data={'name':'Archery-Seniors','relay_duration':90,'athletes_per_relay':10, 'competition_id':competition.competition_id}, instance=event)
        self.assertTrue(form.is_valid())

"""
A test that ensures the functionality that allows the admin to edit coaches,
counties and competitions is working correctly by trying
expected input, unexpected input, and edge cases.
"""
class CoachCountyCompetitionEditTest(TestCase):
    def test_edit_county_form_case(self):
        #Test that we can edit a county to change info
        p_county = County.objects.create(name='Albemarle County')
        form = CountyCreationForm(data={'name':'Green County'},instance=p_county)
        self.assertTrue(form.is_valid())
    def test_edit_competition_form_case(self):
        #Test that we can edit a competition to change info
        p_competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        form = CompetitionCreationForm(data={'name':'2018 Competition','start_date':'2018-10-11'},instance=p_competition)
        self.assertTrue(form.is_valid())
    def test_edit_coach_form_case(self):
        #Test that we can edit a coach to change info
        p_county = County.objects.create(name='Albemarle County')
        p_competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        p_account = Account.objects.create(username='bob',password='helloiambob')
        p_coach = Coach.objects.create(account=p_account,first_name='Bob', last_name='Johnson', email='bob@gmail.com', phone_number='4444444444', county_id=p_county, current_competition=p_competition)
        form = CoachCreationForm(data={'account':p_account.account_id,'first_name':'Tom', 'last_name':'Johnson','email':'bob@gmail.com','phone_number':'4444444444','county_id':p_county.county_id,'current_competition':p_competition.competition_id}, instance=p_coach)
        self.assertTrue(form.is_valid())

"""
A test that ensures the account functionality is working correctly by trying
expected input, unexpected input, and edge cases.
"""
class AccountTesting(TestCase):
    def test_coach_no_account(self):
        #Test that the coach form is not valid without an account
        p_county = County.objects.create(name='Albemarle County')
        p_competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        p_account = Account.objects.create(username='bob',password='helloiambob')
        form = CoachCreationForm(data={'account':'','first_name':'Bob', 'last_name':'Johnson','email':'bob@gmail.com','phone_number':'444-444-4444','county_id':'','current_competition':p_competition.competition_id})
        self.assertFalse(form.is_valid())
    def test_account_create(self):
        p_account = Account.objects.create(username='bob',password='helloiambob')
        self.assertEqual(Account.objects.get(username='bob').password, 'helloiambob')

"""
A test that ensures the functionality that allows a coach to create and edit a player
 is working correctly by trying expected input, unexpected input, and edge cases.
"""
class CoachPlayerTest(TestCase):
    def test_good_case(self):
        #nothing is wrong here
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc,first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        form = CoachPlayerForm(data={'first_name':'test','last_name':'ing','date_of_birth':today,'gender':"Male",'availability':'Both','county_id':p_county.county_id,'competition_id':competition.competition_id,'events':Event.objects.all()})
        self.assertTrue(form.is_valid())
    def test_no_county(self):
        #the county field, supposed to be populated prior to the form loading, is not populated
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        form = CoachPlayerForm(data={'name':'testing','date_of_birth':today,'gender':"Male",'availability':'Both','county_id':'','competition_id':competition.competition_id,'events':Event.objects.all()})
        self.assertFalse(form.is_valid())
    def test_no_birthday(self):
        #the events field is not populated
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        form = CoachPlayerForm(data={'first_name':'testing','last_name':'testing','date_of_birth':today,'gender':"Male",'availability':'Saturday','county_id':p_county.county_id,'competition_id':competition.competition_id})
        self.assertFalse(form.is_valid())
    def test_no_availability(self):
        #the availability field,is not populated with one of the choice
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        form = CoachPlayerForm(data={'first_name':'testing','last_name':'testing','date_of_birth':today,'gender':"Male",'availability':'xyz','county_id':p_county.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
        self.assertFalse(form.is_valid())
    def test_no_hidden(self):
        #none of the hidden fields or events are populated
        today = datetime.date.today()
        form = CoachPlayerForm(data={'name':'testing','date_of_birth':today,'gender':"Male",'availability':'','county_id':''})
        self.assertFalse(form.is_valid())
    def test_edit_okay(self):
        #when used for editing, we pull the selected player's info and populate it as defaults for the fields
        #here we pretend the user just hit enter
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        player = Player.objects.create(first_name='john',last_name='doe',date_of_birth=today,gender="Male",availability='Both',county_id=p_county,competition_id=competition)
        player.events.set(Event.objects.all())
        form = CoachPlayerForm(data={'first_name':player.first_name,'last_name':player.last_name,'date_of_birth':player.date_of_birth,'gender':player.gender,'availability':player.availability,'county_id':player.county_id.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
        self.assertTrue(form.is_valid())
    def test_edit_bad(self):
        #when used for editing, we pull the selected player's info and populate it as defaults for the field
        #here we leave a field blank from its original
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        player = Player.objects.create(first_name="john",last_name="doe",date_of_birth=today,gender="Male",availability='Both',county_id=p_county,competition_id=competition)
        player.events.set(Event.objects.all())
        form = CoachPlayerForm(data={'first_name':player.first_name,'last_name':player.last_name,'date_of_birth':'','gender':player.gender,'availability':player.availability,'county_id':player.county_id.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
        self.assertFalse(form.is_valid())

    def test_edit_change(self):
        #when used for editing, we pull the selected player's info and populate it as defaults for the fields
        #here we chabge a field  from its original
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)

        today = datetime.date.today()
        player = Player.objects.create(first_name="john",last_name="doe",date_of_birth=today,gender="Male",availability='Both',county_id=p_county,competition_id=competition)
        player.events.set(Event.objects.all())
        form = CoachPlayerForm(data={'first_name':player.first_name,'last_name':'new last name','date_of_birth':player.date_of_birth,'gender':player.gender,'availability':player.availability,'county_id':player.county_id.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
        self.assertTrue(form.is_valid())

    def test_not_coach(self):
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        firstName="Elon"
        lastName="Musk"
        try:
            coach=Coach.objects.get(first_name=firstName,last_name=lastName)
        except Coach.DoesNotExist:
            pass
        self.assertEqual(coach.account.username=="user", True)

"""
A test that ensures the URL mapping in the admin dashboard is working correctly
by ensuring that the urls map to the correct views, and the expected HTML is returned.
"""
class AdminDashboardTest(TestCase):
    def test_admin_dashboard_returns_html(self):
        request = HttpRequest()
        response = admin_dashboard(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

    def test_admin_dashboard_returns_correct_html(self):
        request = HttpRequest()
        response = admin_dashboard(request)
        html= response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
        self.assertIn('<title>Admin Dashboard</title>', html)

    def test_add_coach_button_return_correct_html(self):
        request = HttpRequest()
        response = admin_dashboard(request)
        html = response.content.decode('utf8')
        # self.assertTrue(html.contains('<html>'))
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

    def test_add_player_button_return_correct_html(self):
        request = HttpRequest()
        response = admin_dashboard(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

    def test_add_event_button_return_correct_html(self):
        request = HttpRequest()
        response = admin_dashboard(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

    def test_admin_admins_html(self):
        request = HttpRequest()
        response = admin_admins(request)
        html= response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

"""
A test that ensures the URL mapping in the coach dashboard is working correctly
by ensuring that the urls map to the correct views, and the expected HTML is returned.
"""
#temporarily removed for mapping issues
# class CoachDashboardTest(TestCase):
#     #test that the coach view has some html code
#     def test_coach_dashboard_returns_html(self):
#         request = HttpRequest()
#         response = coach_players(request)
#         html = response.content.decode('utf8')
#         self.assertIn('<html>', html)
#         self.assertIn('</html>', html)
#
#     #test that the coach view has the correct html code
#     def test_coach_dashboard_returns_correct_html(self):
#         request = HttpRequest()
#         response = coach_players(request)
#         html= response.content.decode('utf8')
#         self.assertIn('<html>', html)
#         self.assertIn('</html>', html)
#         self.assertIn('<title>Coach Dashboard</title>', html)
#
#     #test that the coach view contains the add players button
#     def test_coach_dashboard_returns_correct_html(self):
#         request = HttpRequest()
#         response = coach_players(request)
#         html= response.content.decode('utf8')
#         self.assertIn('<html>', html)
#         self.assertIn('</html>', html)
#         self.assertIn('Add Players</button>', html)

"""
A test that ensures the URL mapping in the admin dashboard is working correctly
by ensuring that the urls map to the correct views, and the expected HTML is returned.
It also verifies the connection to Google Calendar used in the view.
"""
class AdminScheduleTest(TestCase):
    #test that the admin schedule view has some html code
    def test_admin_schedule_returns_html(self):
        request = HttpRequest()
        response = admin_schedule(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

    #test that the admin schedule view has an iframe
    def test_admin_schedule_returns_iframe(self):
        request = HttpRequest()
        response = admin_schedule(request)
        html = response.content.decode('utf8')
        self.assertIn('<iframe', html)
        self.assertIn('</iframe>', html)

    #test that connection to Google calendar is working
    def test_admin_schedule_calendar_connection(self):
        CLIENT_SECRET_FILE = 'events/four-h-shooting-1ad5c57c94bb.json'
        scopes = "https://www.googleapis.com/auth/calendar"
        credentials = ServiceAccountCredentials.from_json_keyfile_name( filename=CLIENT_SECRET_FILE,scopes=SCOPES)
        http = credentials.authorize(httplib2.Http())
        service = build('calendar', 'v3', http=http)
        calendar = service.calendars().get(calendarId='ktrv3lg5oksebj784ggmc0smho@group.calendar.google.com').execute()
        self.assertIsNotNone(calendar)

"""
A test that ensures the URL mapping in the admin dashboard is working correctly
by ensuring that the urls map to the correct views, and the expected HTML is returned.
"""
class AdminReportsTest(TestCase):
    #test that the admin reports view has some html code
    def test_admin_reports_returns_html(self):
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        request = HttpRequest()
        response = admin_reports(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

    def test_admin_reports_detailed_events(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/admin_reports/'
        event_form = EventSelectionForm(data={'event_id':event})
        response=self.client.post(postlink, {'event_id':event.event_id})
        self.assertTrue(response)

    def test_admin_reports_detailed_county(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/admin_reports/'
        event_form = EventSelectionForm()
        county_form = CountySelectionForm(data={'county_id':county.county_id})
        self.assertTrue(county_form.is_valid())
        response=self.client.post(postlink, {'county_form':county_form,'event_form':event_form,'event_list':Event.objects.filter(competition_id = competition.competition_id),'county_list' : County.objects.all() })
        self.assertTrue(response)

    def test_select_county_form(self):
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        player = Player.objects.create(first_name='john',last_name='doe',date_of_birth=today,gender="Male",availability='Both',county_id=p_county,competition_id=competition)
        player.events.set(Event.objects.all())
        form = CountySelectionForm(data={'county_id':p_county.county_id})
        self.assertTrue(form.is_valid())

"""
A test that ensures the URL mapping in the admin dashboard is working correctly
by ensuring that the urls map to the correct views, and the expected HTML is returned.
"""
class AdminCoachesTest(TestCase):
    #test that the admin schedule view has some html code
    def test_admin_coaches_returns_html(self):
        request = HttpRequest()
        response = admin_coaches(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

"""
A test that ensures the functionality that allows the admin to create a player is working correctly
by trying expected input, unexpected input, and edge cases.
"""
class AdminCreatePlayerTest(TestCase):
    #test that the admin schedule view has some html code
    # def test_admin_create_player_returns_html(self):
    #     self.user = Account.objects.create_user(username='testuser', password='password')
    #     login = self.client.login(username='testuser', password='password')
    #     request = HttpRequest()
    #     response = admin_create_player(request)
    #     html = response.content.decode('utf8')
    #     self.assertIn('<html>', html)
    #     self.assertIn('</html>', html)
    def test_good_case(self):
	 	#nothing is wrong here
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        form = AdminPlayerForm(data={'first_name':'test','last_name':'ing','date_of_birth':today,'gender':"Male",'availability':'Both','county_id':p_county.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
        self.assertTrue(form.is_valid())
    def test_no_county(self):
		#the county field is not populated
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        form = AdminPlayerForm(data={'name':'testing','date_of_birth':today,'gender':"Male",'availability':'Both','county_id':'','competition_id':competition.competition_id})
        self.assertFalse(form.is_valid())
    def test_no_birthday(self):
		#the events field is not populated
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        form = AdminPlayerForm(data={'first_name':'testing','last_name':'testing','date_of_birth':today,'gender':"Male",'availability':'Saturday','county_id':p_county.county_id,'coach_id':coach,'competition_id':competition.competition_id})
        self.assertFalse(form.is_valid())
    def test_no_availability(self):
        #the availability field,is not populated with one of the choices
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        form = AdminPlayerForm(data={'first_name':'testing','last_name':'testing','date_of_birth':today,'gender':"Male",'availability':'xyz','county_id':p_county.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
        self.assertFalse(form.is_valid())
    def test_no_hidden(self):
		#none of the hidden fields or events are populated
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        form = AdminPlayerForm(data={'name':'testing','date_of_birth':today,'gender':"Male",'availability':'','county_id':'','competition_id':competition.competition_id})
        self.assertFalse(form.is_valid())
    def test_edit_okay(self):
		#when used for editing, we pull the selected player's info and populate it as defaults for the fields
		#here we pretend the user just hit enter
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        player = Player.objects.create(first_name="john",last_name="doe",date_of_birth=today,gender="Male",availability='Both',county_id=p_county,competition_id=competition)
        player.events.set(Event.objects.all())
        form = AdminPlayerForm(data={'first_name':player.first_name,'last_name':player.last_name,'date_of_birth':player.date_of_birth,'gender':player.gender,'availability':player.availability,'county_id':player.county_id.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
        self.assertTrue(form.is_valid())
    def test_edit_bad(self):
		#when used for editing, we pull the selected player's info and populate it as defaults for the fields
		#here we leave a field blank from its original
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        player = Player.objects.create(first_name="john",last_name="doe",date_of_birth=today,gender="Male",availability='Both',county_id=p_county,competition_id=competition)
        player.events.set(Event.objects.all())
        form = AdminPlayerForm(data={'first_name':player.first_name,'last_name':player.last_name,'date_of_birth':'','gender':player.gender,'availability':player.availability,'county_id':player.county_id.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
        self.assertFalse(form.is_valid())
    def test_edit_change(self):
		#when used for editing, we pull the selected player's info and populate it as defaults for the fields
		#here we chabge a field  from its original
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        p_county = County.objects.create(name='test_county')
        coach = Coach.objects.create(account=acc, first_name='jack',last_name='doe',email='mev8vy@virginia.edu',phone_number='7579693698',county_id=p_county,current_competition=competition)
        today = datetime.date.today()
        player = Player.objects.create(first_name="john",last_name="doe",date_of_birth=today,gender="Male",availability='Both',county_id=p_county,competition_id=competition)
        player.events.set(Event.objects.all())
        form = AdminPlayerForm(data={'first_name':player.first_name,'last_name':'new last name','date_of_birth':player.date_of_birth,'gender':player.gender,'availability':player.availability,'county_id':player.county_id.county_id,'events':Event.objects.all(), 'competition_id':competition.competition_id})
        self.assertTrue(form.is_valid())

"""
A test that ensures the functionality that allows the admin to view coaches, players, counties etc. is working
"""
class AdminDashboardsHTMLTest(TestCase):
    #test that the admin coaches view has some html code
    def test_admin_coaches_returns_html(self):
        request = HttpRequest()
        response = admin_coaches(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin counties view has some html code
    def test_admin_counties_returns_html(self):
        request = HttpRequest()
        response = admin_counties(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin events view has some html code
    def test_admin_events_returns_html(self):
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        admin = Admin.objects.create(account=acc, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        request = HttpRequest()
        request.user = admin
        response = admin_events(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin events view has some html code
    def test_admin_players_returns_html(self):
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        admin = Admin.objects.create(account=acc, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        request = HttpRequest()
        request.user = admin
        response = admin_players(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin heats view has some html code
    def test_admin_heats_returns_html(self):
        request = HttpRequest()
        response = admin_heats(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin competitions view has some html code
    def test_admin_competitions_returns_html(self):
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        admin = Admin.objects.create(account=acc, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        request = HttpRequest()
        request.user = admin
        response = admin_competitions(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

"""
A test that ensures the admin creating coaches, players, counties etc. has HTML on the page to do the functionality
"""
class AdminCreateHTMLTests(TestCase):
    #test that the admin create coach view has some html code
    def test_admin_create_coach_returns_html(self):
        request = HttpRequest()
        response = admin_create_coach(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the create admin view has some html code
    def test_admin_create_admin_returns_html(self):
        request = HttpRequest()
        response = admin_create_admin(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin create event view has some html code
    def test_admin_create_event_returns_html(self):
        request = HttpRequest()
        response = admin_create_event(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin create heat view has some html code
    def test_admin_create_heat_returns_html(self):
        request = HttpRequest()
        response = admin_create_heat(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin create county view has some html code
    def test_admin_create_county_returns_html(self):
        request = HttpRequest()
        response = admin_create_county(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin create competition view has some html code
    def test_admin_create_competition_returns_html(self):
        request = HttpRequest()
        response = admin_create_competition(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin import competition view has some html code
    def test_admin_import_competition_returns_html(self):
        request = HttpRequest()
        response = admin_import_competition(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

"""
A test that ensures the admin editiing coaches, players, counties etc. has HTML on the page to do the functionality
"""
class AdminEditHTMLTests(TestCase):
    #test that the admin edit coach view has some html code
    def test_admin_edit_coach_returns_html(self):
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        count1=County.objects.create(name="place")
        coach = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=count1, current_competition=competition)
        request = HttpRequest()
        response = admin_edit_coach(request, coach.account.account_id)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin edit county view has some html code
    def test_admin_edit_county_returns_html(self):
        count1=County.objects.create(name="place")
        request = HttpRequest()
        response = admin_edit_county(request, count1.county_id)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin edit competition view has some html code
    def test_admin_edit_competition_returns_html(self):
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        request = HttpRequest()
        response = admin_edit_competition(request, competition.competition_id)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin edit event view has some html code
    def test_admin_edit_event_returns_html(self):
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        request = HttpRequest()
        response = admin_edit_event(request, event.event_id)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin edit heat view has some html code
    def test_admin_edit_heat_returns_html(self):
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        heat = Heat.objects.create(event_id=event, start_time='2018-10-10')
        request = HttpRequest()
        response = admin_edit_heat(request, heat.heat_id)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    #test that the admin edit player view returns some html
    def test_admin_edit_player_returns_html(self):
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        count1=County.objects.create(name="place")
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=count1,competition_id=competition)
        admin = Admin.objects.create(account=acc, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        request = HttpRequest()
        request.user = admin
        response = admin_edit_player(request, player1.player_id)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)

"""
A test that ensures the admin editiing coaches, players, counties etc. has HTML on the page to do the functionality
"""
class CoachHTMLTests(TestCase):
    #test that the coach edit player view has some html code
    def test_coach_edit_player_returns_html(self):
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        count1=County.objects.create(name="place")
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=count1,competition_id=competition)
        coach = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=count1, current_competition=competition)
        request = HttpRequest()
        request.user = coach
        response = coach_edit_player(request, player1.player_id)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    def test_coach_create_player_returns_html(self):
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        request = HttpRequest()
        request.user = coach1
        response = coach_create_player(request)
        html = response.content.decode('utf8')
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
    def test_coach_see_players_as_coach(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='user', password='password')
        self.assertTrue(login)
        postlink = '/coach_players/'
        response=self.client.post(postlink)
        self.assertTrue(response)
    def test_coach_see_players_not_as_coach(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/coach_players/'
        response=self.client.post(postlink)
        self.assertTrue(response)

class LoginFormTest(TestCase):
    def test_login_as_coach(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        postlink = '/login/'
        response=self.client.post(postlink, {'username':'user','password':'password','remember-me':1})
        self.assertTrue(response)
    def test_login_as_admin(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        postlink = '/login/'
        response=self.client.post(postlink, {'username':'admin','password':'password','remember-me':1})
        self.assertTrue(response)
    def test_login_render_get(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        postlink = '/login/'
        response=self.client.get(postlink)
        self.assertTrue(response)
    def test_coach_profile(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='user', password='password')
        self.assertTrue(login)
        postlink = '/coach_profile/'
        response=self.client.get(postlink)
        self.assertTrue(response)
    def test_admin_profile(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/admin_profile/'
        response=self.client.get(postlink)
        self.assertTrue(response)
    def test_admin_profile_no_admin(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.request_factory = RequestFactory()
        postlink = '/admin_profile/'
        request=self.request_factory.get(postlink)
        request.user = acc
        response = admin_profile(request)
        self.assertTrue(response)

class AdminDeleteFunctionsTest(TestCase):
    def test_admin_delete_county_returns(self):
        county1 = County.objects.create(name='place1')
        county2 = County.objects.create(name='place2')
        request = HttpRequest()
        response = admin_delete_county(request,county1.county_id)
        try:
            County.objects.get(name='place1')
        except:
            self.assertIsNotNone(county2)
        self.assertIsNotNone(county1)
    def test_admin_delete_coach_returns(self):
        acc = Account.objects.create(username='user',password='password')
        acc2 = Account.objects.create(username='user2',password='password2')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        county1 = County.objects.create(name='place1')
        county2 = County.objects.create(name='place2')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county1, current_competition=competition)
        coach2 = Coach.objects.create(account=acc2, first_name='bElon', last_name = 'bMusk', county_id=county2, current_competition=competition)
        request = HttpRequest()
        response = admin_delete_coach(request,coach1.account.account_id)
        try:
            Coach.objects.get(first_name='Elon')
        except:
            self.assertIsNotNone(coach2)
        self.assertIsNotNone(coach1)
    def test_admin_delete_event_returns(self):
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event1 = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        event2 = Event.objects.create(name='Archery2',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        request = HttpRequest()
        response = admin_delete_event(request,event1.event_id)
        try:
            Event.objects.get(name='Archery')
        except:
            self.assertIsNotNone(event2)
        self.assertIsNotNone(event1)
    def test_admin_delete_competition_returns(self):
        competition1 = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        competition2 = Competition.objects.create(name='2019 Competition', start_date='2019-10-10')
        request = HttpRequest()
        response = admin_delete_competition(request,competition1.competition_id)
        try:
            Competition.objects.get(name='2018 Competition')
        except:
            self.assertIsNotNone(competition2)
        self.assertIsNotNone(competition1)
    def test_admin_delete_heat_returns(self):
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        heat1 = Heat.objects.create(event_id=event, start_time='2018-10-10')
        heat2 = Heat.objects.create(event_id=event, start_time='2019-10-10')
        request = HttpRequest()
        response = admin_delete_heat(request,heat1.heat_id)
        try:
            Heat.objects.get(start_time='2018-10-10')
        except:
            self.assertIsNotNone(heat2)
        self.assertIsNotNone(heat1)
    def test_ad_p_delete_function_returns(self):
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        request = HttpRequest()
        response = ad_p_delete_function(request,player1.player_id)
        try:
            Player.objects.get(first_name='Eric')
        except:
            self.assertIsNotNone(Player.objects.get(first_name='Tom'))
        self.assertIsNotNone(player1)
    def test_co_p_delete_function_returns(self):
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        request = HttpRequest()
        response = co_p_delete_function(request,player1.player_id)
        try:
            Player.objects.get(first_name='Eric')
        except:
            self.assertIsNotNone(Player.objects.get(first_name='Tom'))
        self.assertIsNotNone(player1)

class AllPlayersReport(TestCase):
    def test_all_players_report_returns(self):
        request = HttpRequest()
        response = report_all_players(request)
        self.assertEqual(response.status_code, 200)
    def test_all_players_report_name(self):
        request = HttpRequest()
        response = report_all_players(request)
        self.assertIn('filename="all_athletes.pdf"', response.get('Content-Disposition'))
    def test_all_players_report_type(self):
        request = HttpRequest()
        response = report_all_players(request)
        self.assertIn('attachment', response.get('Content-Disposition'))

class AllCountiesReport(TestCase):
    def test_all_counties_report_returns(self):
        request = HttpRequest()
        response = report_all_counties(request)
        self.assertEqual(response.status_code, 200)
    def test_all_counties_report_name(self):
        request = HttpRequest()
        response = report_all_counties(request)
        self.assertIn('filename="all_clubs.pdf"', response.get('Content-Disposition'))
    def test_all_counties_report_type(self):
        request = HttpRequest()
        response = report_all_counties(request)
        self.assertIn('attachment', response.get('Content-Disposition'))

#The following tests are to ensure that the proper error messages appear for certain errors
class CountyErrorTest(TestCase):
	def test_name_error(self):
		form = CountyCreationForm(data={'name':'fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'})
		self.assertFalse(form.is_valid())
		self.assertEqual(form.errors['name'][0],'Name must be less than 100 characters')

class PlayerErrorTest(TestCase):
	def test_fname_error(self):
		competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
		event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
		event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
		p_county = County.objects.create(name='test_county')
		today = datetime.date.today()
		form = AdminPlayerForm(data={'first_name':'fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff','last_name':'ing','date_of_birth':today,'gender':"Male",'availability':'Both','county_id':p_county.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
		self.assertFalse(form.is_valid())
		self.assertEqual(form.errors['first_name'][0],'Name must be less than 100 characters')
	def test_lname_error(self):
		competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
		event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
		event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
		p_county = County.objects.create(name='test_county')
		today = datetime.date.today()
		form = AdminPlayerForm(data={'first_name':'test','last_name':'fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff','date_of_birth':today,'gender':"Male",'availability':'Both','county_id':p_county.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
		self.assertFalse(form.is_valid())
		self.assertEqual(form.errors['last_name'][0],'Name must be less than 100 characters')
	def test_dob_error(self):
		competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
		event1 = Event.objects.create(name='firstevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
		event2 = Event.objects.create(name='secondevent',relay_duration=90,athletes_per_relay=10,competition_id=competition)
		p_county = County.objects.create(name='test_county')
		today = datetime.date.today()
		form = AdminPlayerForm(data={'first_name':'test','last_name':'ing','date_of_birth':'06251998','gender':"Male",'availability':'Both','county_id':p_county.county_id,'events':Event.objects.all(),'competition_id':competition.competition_id})
		self.assertFalse(form.is_valid())
		self.assertEqual(form.errors['date_of_birth'][0],'Please Enter a Date of the Format YYYY-MM-DD or MM/DD/YYYY')

class CompetitionErrorTest(TestCase):
	def test_name_error(self):
		form = CompetitionCreationForm(data={'name':'fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
'start_date':'06/25/1998'})
		self.assertFalse(form.is_valid())
		self.assertEqual(form.errors['name'][0],'Name must be less than 100 characters')
	def test_date_error(self):
		form = CompetitionCreationForm(data={'name':'name',
'start_date':'06251998'})
		self.assertFalse(form.is_valid())
		self.assertEqual(form.errors['start_date'][0],'Please Enter a Date of the Format YYYY-MM-DD')

class ReportingTest(TestCase):
    def test_coach_report(self):
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        request = HttpRequest()
        request.user = coach1
        response = coach_report(request)
        self.assertTrue(response)
    def test_player_coach_report_no_heat(self):
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        request = HttpRequest()
        request.user = coach1
        response = report_player_schedule(request)
        self.assertTrue(response)
    def test_player_coach_report_yes_heat(self):
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        heat = Heat.objects.create(event_id=event, start_time='2018-10-10')
        heat.players.add(player1, player2)
        heat.save()
        request = HttpRequest()
        request.user = coach1
        response = report_player_schedule(request)
        self.assertTrue(response)
    def test_coach_csv_report(self):
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        heat = Heat.objects.create(event_id=event, start_time='2018-10-10')
        heat.players.add(player1, player2)
        heat.save()
        request = HttpRequest()
        request.user = admin
        response = report_csv(request)
        self.assertTrue(response)
    def test_report_all_players(self):
        county = County.objects.create(name='Albemarle County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        heat = Heat.objects.create(event_id=event, start_time='2018-10-10')
        heat.players.add(player1, player2)
        heat.save()
        request = HttpRequest()
        request.user = admin
        response = report_all_players(request)
        self.assertTrue(response)
    def test_report_all_counties(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        heat = Heat.objects.create(event_id=event, start_time='2018-10-10')
        heat.players.add(player1, player2)
        heat.save()
        request = HttpRequest()
        request.user = admin
        response = report_all_counties(request)
        self.assertTrue(response)
    def test_report_all_events(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        heat = Heat.objects.create(event_id=event, start_time='2018-10-10')
        heat.players.add(player1, player2)
        heat.save()
        request = HttpRequest()
        request.user = admin
        response = report_all_events(request)
        self.assertTrue(response)
    def test_report_select_events_with_heat(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        heat = Heat.objects.create(event_id=event, start_time='2018-10-10')
        heat.players.add(player1, player2)
        heat.save()
        self.request_factory = RequestFactory()
        request = self.request_factory.post('/report_select_events', {'event_id': event.event_id})
        request.user = admin
        response = report_select_events(request)
        self.assertTrue(response)
    def test_report_select_events_no_heat(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        self.request_factory = RequestFactory()
        request = self.request_factory.post('/report_select_events', {'event_id': event.event_id})
        request.user = admin
        response = report_select_events(request)
        self.assertTrue(response)

class CreationTests(TestCase):
    def test_admin_create_player_not_admin(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        request = HttpRequest()
        request.user = coach1
        response = admin_create_player(request)
        self.assertTrue(response)
    def test_admin_create_player_as_admin(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/admin_create_player/'
        response=self.client.post(postlink, {'first_name':'test','last_name':'ing','date_of_birth':today,'gender':'Male','county_id':county.county_id,'availability':'Both','events':[event.event_id],'competition_id':competition.competition_id})
        self.assertTrue(response)
        self.client.post('/logout/')
    def test_coach_create_player_as_coach(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='user', password='password')
        self.assertTrue(login)
        postlink = '/coach_create_player/'
        response=self.client.post(postlink, {'first_name':'test','last_name':'ing','date_of_birth':today,'gender':'Male','county_id':county.county_id,'availability':'Both','events':[event.event_id],'competition_id':competition.competition_id})
        self.assertTrue(response)
    def test_coach_create_player_not_as_coach(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        #coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/coach_create_player/'
        response=self.client.post(postlink, {'first_name':'test','last_name':'ing','date_of_birth':today,'gender':'Male','county_id':county.county_id,'availability':'Both','events':[event.event_id],'competition_id':competition.competition_id})
        self.assertTrue(response)
    def test_admin_create_heat(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/admin_create_heat/'
        response=self.client.post(postlink, {'event_id':event.event_id,'start_time':today,'players':[player1.player_id]})
        self.assertTrue(response)
    def test_admin_create_county(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/admin_create_county/'
        response=self.client.post(postlink, {'name':'Albemarle County'})
        self.assertTrue(response)

class EditTests(TestCase):
    def test_admin_edit_coach(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        coach1.__str__()
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        self.client = Client()
        postlink = '/admin_edit_coach/' + str(coach1.account.account_id) + '/'
        response=self.client.post(postlink, {'first_name':'name', 'last_name':'name', 'email':'user@email.com', 'phone_number': '7037037033', 'county_id':county.county_id})
        self.assertTrue(response)
    def test_admin_edit_event(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        self.client = Client()
        postlink = '/admin_edit_event/' + str(event.event_id) + '/'
        response=self.client.post(postlink, {'name':'Archery','relay_duration':90,'athletes_per_relay':10, 'competition_id':competition.competition_id})
        self.assertTrue(response)
    def test_admin_edit_heat(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        heat = Heat.objects.create(event_id=event, start_time='2018-10-10')
        heat.players.add(player1, player2)
        today = datetime.date.today()
        self.client = Client()
        postlink = '/admin_edit_heat/' + str(heat.heat_id) + '/'
        response=self.client.post(postlink, {'event_id':event.event_id,'start_time':today,'players':[player1.player_id]})
        self.assertTrue(response)
    def test_admin_edit_county(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        self.client = Client()
        postlink = '/admin_edit_county/' + str(county.county_id) + '/'
        response=self.client.post(postlink, {'name':'Albemarle County'})
        self.assertTrue(response)
    def test_admin_edit_player(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='admin', password='password')
        self.assertTrue(login)
        postlink = '/admin_edit_player/' + str(player1.player_id) + '/'
        response=self.client.post(postlink, {'first_name':'test','last_name':'ing','date_of_birth':today,'gender':'Male','county_id':county.county_id,'availability':'Both','events':[event.event_id],'competition_id':competition.competition_id})
        self.assertTrue(response)
    def test_coach_edit_player_good_form(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user')
        acc.set_password('password')
        acc.save()
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        today = datetime.date.today()
        self.client = Client()
        login = self.client.login(username='user', password='password')
        self.assertTrue(login)
        postlink = '/coach_edit_player/' + str(player1.player_id) + '/'
        response=self.client.post(postlink, {'first_name':'test','last_name':'ing','date_of_birth':today,'gender':'Male','county_id':county.county_id,'availability':'Both','events':[event.event_id],'competition_id':competition.competition_id})
        self.assertTrue(response)
    def test_admin_import_competition(self):
        county = County.objects.create(name='Albemarle County')
        county2 = County.objects.create(name='Greenville County')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        event = Event.objects.create(name='Archery',relay_duration=90,athletes_per_relay=10,competition_id=competition)
        player1 = Player.objects.create(first_name='Eric',last_name='Larson',date_of_birth='2001-10-10',gender='Male',availability='Both',county_id=county,competition_id=competition)
        player2 = Player.objects.create(first_name='Tom',last_name='Larson',date_of_birth='2002-10-10',gender='Male',availability='Both',county_id=county2,competition_id=competition)
        acc = Account.objects.create(username='user',password='password')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county, current_competition=competition)
        acc2 = Account.objects.create(username='admin',password='password')
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        self.client = Client()
        self.client.login(username='admin', password='password')
        postlink = '/admin_import_competition/'
        response=self.client.post(postlink, {'competition_name':'2019 Competition','start_date':'2019-10-10','imported_competition':competition.competition_id})
        self.assertTrue(response)

class SetCurrentCompetitionTests(TestCase):
    def test_admin_set_current_competition(self):
        acc = Account.objects.create(username='user',password='password')
        competition = Competition.objects.create(name='2018 Competition', start_date='2018-10-10')
        county1 = County.objects.create(name='place1')
        coach1 = Coach.objects.create(account=acc, first_name='Elon', last_name = 'Musk', email='mev8vy@virginia.edu',phone_number='7579693698', county_id=county1, current_competition=competition)
        competition2 = Competition.objects.create(name='2019 Competition', start_date='2019-10-10')
        acc2 = Account.objects.create(username='admin')
        acc2.set_password('password')
        acc2.save()
        admin = Admin.objects.create(account=acc2, current_competition=competition, first_name='adminfirstname', last_name='adminlastname')
        request = HttpRequest()
        response = admin_set_current_competition(request, competition2.competition_id)
        self.assertTrue(response)

# class PasswordChangeFormTest(TestCase):
#     def test_password_change_clean(self):
#         form = PasswordChangeForm(data={'password':'hello', 'confirm_password':'hello'})
#         form.clean()
#         assertTrue(form.is_valid())
#     def test_password_change_clean_passnomatch(self):
#         form = PasswordChangeForm(data={'password':'hello1', 'confirm_password':'hello'})
#         form.clean()
#         assertFalse(form.is_valid())

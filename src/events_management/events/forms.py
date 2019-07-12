"""
This is the dedicated django file for placing the forms we use in our app.
Due to the nature of our application, these forms are closely related to our models
and thus there will frequently be a form that maps directly to a model object.
"""

from django import forms
from events.models import Coach, County, Competition, Player, Account, Event, Heat, Admin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _

"""
A form that allows to create a user in the system. This is done indirectly
whenever an admin or a coach is created.
"""
class CustomUserCreationForm(UserCreationForm):
	class Meta:
		model = Account
		fields = ('username', )

"""
A form that allows to change a user in the system. This is done indirectly
whenever an admin or a coach modifies their profile.
"""
class CustomUserChangeForm(UserChangeForm):
	class Meta:
		model = Account
		fields = ('username', )

"""
A form that allows to create an admin user in the system. The admin has access to
this form, in order to create other users with admin permissions.
"""
class AdminCreationForm(forms.ModelForm):
    #first_name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
    #last_name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
    #email = forms.CharField(error_messages = {'max_length':'Email must be less than 200 characters'})
    #phone_number = forms.CharField(error_messages= {'invalid_phone':'Please enter a phone number of the format XXXXXXXXXX'})
	class Meta:
		model = Admin
		fields = ('first_name', 'last_name', 'email', 'phone_number')
		widgets = {
			'email':forms.EmailInput(),
		}
		labels = {
			'first_name':_('First Name'),
			'last_name':_('Last Name'),
			'email':_('Email'),
			'phone_number':_('Phone Number'),
		}
		help_texts = {
			'phone_number':_('No parentheses or dashes (i.e. 123456890)'),
		}
		error_messages = {
			'first_name':{
				'max_length':_("Name must be less than 100 characters"),

			},
			'last_name':{
				'max_length':_("Name must be less than 100 characters"),

			},
			'phone_number':{
				'invalid_phone':_ ("Please enter a phone number of the format XXXXXXXXXX"),
			},

		}
"""
A form that allows to create a acounty in the system. The admin is able to do
this from the County tab in the admin dashboard.
"""
#name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
class CountyCreationForm(forms.ModelForm):
	class Meta:
		model = County
		fields = ('name', )
		labels = {
			'name':_('County/Club Name'),
		}
		error_messages={
			'name':{
				'max_length':_("Name must be less than 100 characters"),
			}
		}
"""
A form that allows to create a coach in the system. The admin performs this action
from the Coach tab of the admin dashboard.
"""
class CoachCreationForm(forms.ModelForm):
   # first_name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
    #last_name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
    #email = forms.CharField(error_messages = {'max_length':'Email must be less than 200 characters'})
    #phone_number = forms.CharField(error_messages= {'invalid_phone':'Please enter a phone number of the format XXXXXXXXXX'})
	class Meta:
		model = Coach
		fields = ('first_name', 'last_name', 'email', 'phone_number','county_id', )
		widgets = {
			'email':forms.EmailInput(),
		}
		labels = {
				'first_name':_('First Name'),
				'last_name':_('Last Name'),
				'email':_('Email'),
				'phone_number':_('Phone Number'),
			}
		help_texts = {
			'phone_number':_('No parentheses or dashes (i.e. 123456890)'),
		}
		error_messages = {
			'first_name':{
				'max_length':_("Name must be less than 100 characters"),

			},
			'last_name':{
				'max_length':_("Name must be less than 100 characters"),

			},
			'phone_number':{
				'invalid_phone':_ ("Please enter a phone number of the format XXXXXXXXXX"),
			},

		}

class PasswordChangeForm(forms.ModelForm):
	password=forms.CharField(widget=forms.PasswordInput())
	confirm_password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = Account
		fields = ('password', )

	def clean(self):
		cleaned_data = super(PasswordChangeForm, self).clean()
		password = cleaned_data.get("password")
		confirm_password = cleaned_data.get("confirm_password")

		if password != confirm_password:
			raise forms.ValidationError(
				"Passwords do not match"
			)
		return cleaned_data

"""
A form that allows to create an event in the system. The admin performs this action
from the Events tab of the admin dashboard.
"""
class EventCreationForm(forms.ModelForm):
   # name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
	class Meta:
		model = Event
		fields = ('name', 'relay_duration', 'athletes_per_relay', 'competition_id',)
		labels = {
					'name':_('Event Name'),
					'relay_duration':_('Duration of Relay in Minutes'),
					'athletes_per_relay':_('Athletes Per Relay'),
					'competition_id':_('Associated Competition'),
				}

		error_messages = {
			'name':{
				'max_length':_("Name must be less than 100 characters"),

			},

		}

"""
A form that allows to create a heat in the system. The admin performs this action
from the Heats tab of the admin dashboard.
"""
class HeatCreationForm(forms.ModelForm):
    #start_time = forms.DateTimeField(error_messages={'invalid':'Please enter a date and time of the format yyyy-mm-dd hh:mm:ss'})
	class Meta:
		model = Heat
		fields = ('event_id', 'start_time', 'players',)
		labels = {
			'event_id':_('Associated Event'),
			'start_time':_('Event Start Time'),
			'players':_('Enrolled Players'),
		}
		help_texts = {
			'start_time':_('yyyy-mm-dd hh:mm:ss'),
		}
		error_messages = {
			'start_time':{
				'invalid':_ ("Please enter a date and time of the format yyyy-mm-dd hh:mm:ss"),
			},
		}

"""
A form that allows to edit a coach record in the system. The admin performs this action
from the Coach tab of the admin dashboard.
"""
class CoachEditForm(forms.ModelForm):
	#first_name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
	#last_name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
	#email = forms.CharField(error_messages = {'max_length':'Email must be less than 200 characters'})
	#phone_number = forms.CharField(error_messages= {'invalid_phone':'Please enter a phone number of the format XXXXXXXXXX'})
	class Meta:
		model = Coach
		fields = ('first_name', 'last_name', 'email', 'phone_number',
		'county_id', )
		labels = {
				'first_name':_('First Name'),
				'last_name':_('Last Name'),
				'email':_('Email'),
				'phone_number':_('Phone Number'),
			}
		help_texts = {
			'phone_number':_('No parentheses or dashes (i.e. 123456890)'),
		}
		error_messages = {
			'first_name':{
				'max_length':_("Name must be less than 100 characters"),

			},
			'last_name':{
				'max_length':_("Name must be less than 100 characters"),

			},
			'phone_number':{
				'invalid_phone':_ ("Please enter a phone number of the format XXXXXXXXXX"),
			},

		}

"""
A form that allows to create a competition in the system. The admin performs this action
from the Competitions tab of the admin dashboard.
"""
class CompetitionCreationForm(forms.ModelForm):
	class Meta:
		model = Competition
		fields = ('name', 'start_date', )
		labels = {
			'name':_('Competition Name'),
			'start_date':_('Competition Start Date'),
		}
		help_texts = {
			'start_date':_('yyyy-mm-dd'),
		}
		error_messages = {
			'name':{
				'max_length':_("Name must be less than 100 characters"),

			},
			'start_date':{
				'invalid':_ ("Please Enter a Date of the Format YYYY-MM-DD"),
			},
		}
	 ## name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
   # start_date = forms.DateField(error_messages = {'invalid':'Please Enter a date of the format dd-mm-yyyy'})

"""
A form that allows to create a competition in the system. The admin performs this action
from the Competitions tab of the admin dashboard.
"""
class CompetitionImportForm(forms.Form):
	competition_name = forms.CharField(max_length=100)
	start_date = forms.DateField()
	imported_competition = forms.ModelChoiceField(queryset=Competition.objects.all())

"""
This form is indirectly used as a part of other forms. It allows to create a
county dropdown for better usability.
"""
class CountySelectionForm(forms.ModelForm):
	class Meta:
		model = Player
		fields = ('county_id', )

	def __init__ (self, *args,**kwargs):
		super(CountySelectionForm,self).__init__(*args,**kwargs)
		self.fields["county_id"].label = ""
		self.fields["county_id"].widget=forms.widgets.Select()
		self.fields["county_id"].empty_label = None
		self.fields["county_id"].queryset=County.objects.all()

"""
This form is indirectly used as a part of other forms. It allows to create
an event select for better usability.
"""
class EventSelectionForm(forms.ModelForm):
	class Meta:
		model = Heat
		fields = ('event_id', )

	def __init__ (self, *args,**kwargs):
		super(EventSelectionForm,self).__init__(*args,**kwargs)
		self.fields["event_id"].label = ""
		self.fields["event_id"].widget=forms.widgets.SelectMultiple()
		self.fields["event_id"].empty_label = None
		self.fields["event_id"].queryset=Event.objects.all()

"""
A form that allows the admin to create a player in the system, as a member of
any coach's team. The admin has access to this form from the Players tab of the
admin dashboard.
"""
class AdminPlayerForm(forms.ModelForm):
	#first_name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
	#last_name = forms.CharField(error_messages= {'max_length':'Name must be less than 100 characters'})
	#date_of_birth = forms.DateField(error_messages = {'invalid':'Please Enter a date of the format dd-mm-yyyy'})
	#events =
	class Meta:
		model = Player
		fields = [
			'first_name',
			'last_name',
			'date_of_birth',
			'gender',
			'county_id',
			#'player_id',
			'availability',
			#'user_id',
			'events',
			'competition_id',
		]
		labels = {
			'first_name':_('First Name'),
			'last_name':_('Last Name'),
			'date_of_birth':_('Date of Birth'),
			'gender':_('Gender'),
			'county_id':_('County/Club'),
			'availability':_('Player Availability'),
			'events':_('Requested Events'),
			'competition_id':_('Associated Competition'),
		}
		help_texts = {
			'date_of_birth':_('Must be of Format yyyy-mm-dd or mm/dd/yyyy'),
		}
		error_messages = {
			'first_name':{
				'max_length':_("Name must be less than 100 characters"),


			},
			'last_name':{
				'max_length':_("Name must be less than 100 characters"),


			},
			'date_of_birth':{
				'invalid':_ ("Please Enter a Date of the Format YYYY-MM-DD or MM/DD/YYYY"),
			},
		}
	def __init__ (self, *args,**kwargs):
		super(AdminPlayerForm,self).__init__(*args,**kwargs)


		#self.fields["county_id"].queryset=County.objects.filter(county_id =)
		self.fields["events"].widget=forms.widgets.CheckboxSelectMultiple()
		self.fields["events"].queryset= Event.objects.all()
		self.fields["county_id"].widget=forms.widgets.Select()
		self.fields["county_id"].queryset=County.objects.all()
		self.fields["competition_id"].queryset = Competition.objects.all()

"""
A form that allows the coach to create a player in the system, as a member of
their team. The coach has access to this form from their dashboard.
"""
class CoachPlayerForm(forms.ModelForm):
	requested_asset = None
	#admin version will be similar, but also include fields for coach and county
	#player_id = forms.CharField(required=False)
	#availability=forms.CharField(required=False)
	#county_id = forms.CharField(required=False)
	class Meta:
		model = Player
		fields = [
			'first_name',
			'last_name',
			'date_of_birth',
			'gender',
			#'player_id',
			'availability',
			#'user_id',
			'events',
			#'county_id',
			#'competition_id',
		]
		labels = {
			'first_name':_('First Name'),
			'last_name':_('Last Name'),
			'date_of_birth':_('Date of Birth'),
			'gender':_('Gender'),
			#'county_id':_('County/Club'),
			'availability':_('Player Availability'),
			'events':_('Requested Events'),
			#'competition_id':_('Associated Competition'),
		}
		help_texts = {
			'date_of_birth':_('Must be of Format yyyy-mm-dd or mm/dd/yyyy'),
		}
		error_messages = {
			'first_name':{
				'max_length':_("Name must be less than 100 characters"),


			},
			'last_name':{
				'max_length':_("Name must be less than 100 characters"),


			},
			'date_of_birth':{
				'invalid':_ ("Please Enter a Date of the Format YYYY-MM-DD or MM/DD/YYYY"),
			},
		}

	def __init__ (self, *args,**kwargs):
		super(CoachPlayerForm,self).__init__(*args,**kwargs)
		# self.fields["coach_id"].widget=forms.widgets.CheckboxSelectMultiple()
		#self.fields["county_id"].queryset = County.objects.all()
		#self.fields["county_id"].widget = forms.HiddenInput()
		#self.fields["competition_id"].queryset = Competition.objects.all()
		#self.fields["competition_id"].widget = forms.HiddenInput()
		self.fields["events"].widget=forms.widgets.CheckboxSelectMultiple()
		self.fields["events"].queryset= Event.objects.all()

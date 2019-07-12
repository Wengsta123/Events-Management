"""
This is the standard django file for the models of our application. All models
here reflect objects we have used to model the application, and they are reflected
in a table of our database.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
"""
This represents a county, or more accurately a club that can
participate in the event. The only relevant information is the
club or county name.
"""
class County(models.Model):
    county_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default = "")

    def __str__(self):
        return self.name

"""
This is an instance of the State Shoot. We expect there would
be one competition per year.
"""
class Competition(models.Model):
    competition_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default = "")
    start_date = models.DateField()

    def __str__(self):
        return self.name

"""
This is a user account that allows us to log in to the site. It
contains only basic information such as password and username.
"""
class Account(AbstractUser):
    USERNAME_FIELD = 'username'
    account_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64,unique=True)
    password = models.CharField(max_length=64)

    def __str__(self):
        return self.username

"""
This is an event where players can choose to participate. An example would be
archery. Each event has information regarding the heats that will be dedicated
to it, like heat duration and number of player per heat. Each event belongs to
a competition.
"""
class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    relay_duration = models.IntegerField(default=0) #the duration of a heat of this event
    athletes_per_relay = models.IntegerField(default=0) #players per heat
    competition_id = models.ForeignKey(Competition, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

"""
A student could be available for either Saturday, Sunday or both days.
As far as we know, all competitions take place during the weekend.
"""
AVAILABILITY_CHOICES= (
	('Saturday','Saturday'),
	('Sunday','Sunday'),
	('Both','Both'),
)

"""
This is a team's coach (or coach of record). This user will have access to the
system and be able to see the players in their team from the coach dashboard.
This model contains all the information an admin would need about the coach.
"""
class Coach(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=100, error_messages = {'blank':'Please enter a Name'})
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
#Validator ensures a consistent format for phone numbers, making it less confusing for the user.
    phone_number = models.CharField(max_length=12, validators=[RegexValidator('^(\d{10})$',message='Please enter a phone number of the format XXXXXXXXXX', code = 'invalid_phone')])
    county_id = models.ForeignKey(County, on_delete=models.CASCADE)
    current_competition = models.ForeignKey(Competition, on_delete=models.CASCADE)

    def __str__(self):
        return self.first_name + " " + self.last_name



"""
The customer requested that gender be selected as a dropdown with the following choices to simplify housing arrangements for players
"""
GENDER_CHOICES= (
	('Male','Male'),
	('Female','Female'),
	('Other/No Answer','Other/No Answer'),
)


"""
This is a player, or participant in the State Shoot. They belong to a coach's
team and to a county or club. They do not have access to the system, instead
their coaches or the admin will edit their information for them. Players will
request to participate in events, which the scheduler will attempt to accomodate
for. This contains all the information we need to place players into heats.
"""
class Player(models.Model):
    player_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=16, choices = GENDER_CHOICES, default = 'Other/No Answer')
    availability = models.CharField(max_length=8,choices=AVAILABILITY_CHOICES,default='Saturday')
    county_id = models.ForeignKey(County, on_delete=models.CASCADE)
    competition_id = models.ForeignKey(Competition, on_delete=models.CASCADE)
    events = models.ManyToManyField(Event)

    def __str__(self):
        return self.first_name + " " + self.last_name

# class EventManager(models.Model):
#     event_manager_id = models.AutoField(primary_key=True)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     phone_number = models.CharField(max_length=10,blank=True)

"""
This is a single occurrence of an event. For example, the event would be archery,
and the heat will start at 9, end at 10 and players in that heat will be participating
in the archery event.
"""
class Heat(models.Model):
    heat_id = models.AutoField(primary_key=True)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    #duration = models.IntegerField(), this field was commented out since it's inherited from 
    #the associated event
    players = models.ManyToManyField(Player)

"""
This is the asministrator of the site. There could be more than one. All admins
will have access to virtually all the information in the system. This would be
the role played by the customer once the application is in production.
"""
class Admin(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    current_competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, default = " ")
    last_name = models.CharField(max_length=100, default = " ")
    email = models.CharField(max_length=200, default = " ")
    phone_number = models.CharField(max_length=12, default = " ", validators=[RegexValidator('^(\d{10})$',message='Please enter a phone number of the format XXXXXXXXXX', code = 'invalid_phone')])

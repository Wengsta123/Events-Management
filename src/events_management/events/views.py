"""
This is the views file, which constitutes the logic layer of our application.
Some of the views listed here are used to render pages with the correct data,
some views are used as proxies for displaying and submitting forms, and yet others
are used to render and download reports that the user can save as PDF files.
"""
from django.shortcuts import render,redirect
from django.template import Template, Context
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib import sessions, messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.views.generic.edit import UpdateView
from events.forms import EventSelectionForm, CoachPlayerForm, CountySelectionForm, CoachCreationForm, CountyCreationForm, CompetitionCreationForm, CompetitionImportForm, CoachPlayerForm, AdminPlayerForm, EventCreationForm, HeatCreationForm, CustomUserCreationForm, AdminCreationForm, PasswordChangeForm
from events.models import County, Coach, Competition, Player, Account, Event, Heat, Admin
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.core.files.storage import FileSystemStorage
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
from datetime import timedelta
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import pytz
import os
import csv

#global
service_account_email = 'four-h-shooting@four-h-shooting.iam.gserviceaccount.com'
CLIENT_SECRET_FILE = 'events/four-h-shooting-1ad5c57c94bb.json'
SCOPES = 'https://www.googleapis.com/auth/calendar'
scopes = [SCOPES]

def start_scheduler(request):
    # if the scheduler doesn't exist, compile it
    if (os.path.isfile("./scheduler/scheduler")):
        os.scandir("scheduler/")
    else:
        make_status = os.system('make -C scheduler')
        if (make_status != 0):
            print('error: compilation error')
    scheduler_status = 256
    # error because of scheduler-database miss handling
    while (scheduler_status == 256):
        scheduler_status = os.system('./scheduler/scheduler ./db.sqlite3') # restart the scheduler
        if (scheduler_status == 256):
            print('error: scheduler had a database miss')
            print('INFO: restarting the scheduler')
    if (scheduler_status != 0):
        print('error: (' + str(scheduler_status) + ') other scheduler error')

    # return the schedule page
    context = {
	'event_list': Event.objects.all(),
    }
    return HttpResponse(render(request,'admin_schedule.html',context))

def refresh_schedule(request):
    #connecting to the calendar
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        filename=CLIENT_SECRET_FILE,
        scopes=SCOPES
    )

    http = credentials.authorize(httplib2.Http())
    service = build('calendar', 'v3', http=http)

    #clearing the calendar
    page_token = None
    while True:
      events = service.events().list(calendarId='ktrv3lg5oksebj784ggmc0smho@group.calendar.google.com', pageToken=page_token).execute()
      for event in events['items']:
        # print event['summary']
        service.events().delete(calendarId='ktrv3lg5oksebj784ggmc0smho@group.calendar.google.com', eventId=event['id']).execute()
      page_token = events.get('nextPageToken')
      if not page_token:
        break

    #logging all heats in database
    heats = Heat.objects.all()
    for heat in heats:
        #start time
        start = heat.start_time
        local_tz = pytz.timezone ("America/New_York")
        datetime_without_tz = datetime.datetime.strptime(str(start)[:19], "%Y-%m-%d %H:%M:%S")
        start = local_tz.localize(datetime_without_tz, is_dst=None) # No daylight saving time
        start = str(start)
        new = list(start)
        new[10] = 'T'
        start = ''.join(new)
        #end time
        end = heat.start_time + timedelta(minutes = heat.event_id.relay_duration)
        datetime_without_tz = datetime.datetime.strptime(str(end)[:19], "%Y-%m-%d %H:%M:%S")
        end = local_tz.localize(datetime_without_tz, is_dst=None) # No daylight saving time
        end = str(end)
        new = list(end)
        new[10] = 'T'
        end = ''.join(new)
        #event name
        summary = heat.event_id.competition_id.name + " - " + heat.event_id.name
        event = {
          'summary': str(summary),
          'start': {
            'dateTime': str(start),
            'timeZone': 'America/New_York',
          },
          'end': {
            'dateTime': str(end),
            'timeZone': 'America/New_York',
          },
        }
        event = service.events().insert(calendarId='ktrv3lg5oksebj784ggmc0smho@group.calendar.google.com', body=event).execute()
        # print ('Event created: %s' % (event.get('htmlLink')))

    return redirect('admin_schedule')

"""
This view generates and downloads a PDF file containing the schedule information for players assigned to
the club that the logged in coach is assigned.
"""

def report_player_schedule(request):
    response = HttpResponse(content_type='application/pdf')
    account = request.user.account_id
    coach = Coach.objects.get(account_id=account)
    coachPlayers = Player.objects.filter(county_id=coach.county_id).order_by('last_name')
    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    header = Paragraph(str(coach.county_id), style)
    response['Content-Disposition'] = 'attachment; filename='+str(coach.county_id)+'_Player_Schedules.pdf'
    p = canvas.Canvas(response)
    p.setTitle('Player Schedules')
    heats = Heat.objects.all().order_by('start_time')
    """
    This section accesses the information for each player assigned to the currently logged in coach
    and compared this info to that stored in heats to create a list of all heats that each player has been
    assigned to create their schedule.
    """
    if len(heats) != 0:
        for player in coachPlayers:
            current_competition = coach.current_competition
            if current_competition == player.competition_id:
                header = Paragraph(str(player.first_name)+" "+str(player.last_name)+" Schedule", style)
                y = 50
                data = [["Event","Heat", "Time"]]
                for heat in heats:
                    for heatPlayer in heat.players.all():
                        if heatPlayer.player_id==player.player_id:
                            data.append([str(heat.event_id.name), str(heat.heat_id), str(heat.start_time)])
                        t = Table(data)
                        data_len = len(data)
                for each in range(data_len):
                    if each % 2 == 0:
                        bg_color = colors.whitesmoke
                    else:
                        bg_color = colors.lightgrey
                    t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))
                aW = 540
                aH = 720
                w, h = header.wrap(aW, aH)
                header.drawOn(p, 72, aH)
                aH = aH - h
                w, h = t.wrap(aW, aH)
                t.drawOn(p, 72, aH-(1.1*h))
                y = y + 100
                p.showPage()
                data = [[]]
    else:
        aW = 540
        aH = 720
        data = [["Schedule has not yet been created by admin"]]
        t = Table(data)
        w, h = t.wrap(aW, aH)
        t.drawOn(p, 72, aH)
        p.showPage()
    p.save()
    return response

"""
This view generates and downloads a PDF file containing the information for players assigned to
the club that the logged in coach is assigned.
"""

def coach_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="coach_report.pdf"'
    account = request.user.account_id
    coach = Coach.objects.get(account_id=account)
    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    p = canvas.Canvas(response)
    p.setTitle("Coach Report")
    query = Player.objects.filter(county_id=coach.county_id).order_by('last_name')
    header = Paragraph(str(coach.county_id), style)
    y = 50
    data = [["Athlete ID", "First Name","Last Name","Date of Birth","Gender","Club","Availability"]]
    for player in query:
        current_competition = coach.current_competition
        if player.competition_id == current_competition:
            data.append([str(player.player_id), str(player.first_name), str(player.last_name), str(player.date_of_birth), str(player.gender), str(player.county_id), str(player.availability)])
    t = Table(data)
    data_len = len(data)
    for each in range(data_len):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey
        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))
    aW = 540
    aH = 720
    w, h = header.wrap(aW, aH)
    header.drawOn(p, 72, aH)
    aH = aH - h
    w, h = t.wrap(aW, aH)
    t.drawOn(p, 72, aH-h)
    y = y + 100
    p.showPage()
    p.save()
    return response

"""
This view generates and downloads a PDF file containing the information for the
schedule of the county the user has selected.
"""
def report_select_county(request):
    response = HttpResponse(content_type='application/pdf')
    county_selection = request.POST.get('county_id', None)
    if county_selection:
        county_name = str(County.objects.get(county_id=county_selection))
    else:
        county_name = "NULL"
    response['Content-Disposition'] = 'attachment; filename='+county_name+"_Athletes.pdf"

    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    p = canvas.Canvas(response)
    p.setTitle(county_name)
    query = Player.objects.filter(county_id=county_selection).order_by('last_name')
    header = Paragraph(county_name, style)
    y = 50
    data = [["Athlete ID", "First Name","Last Name","Date of Birth","Gender","Club","Availability"]]

    for player in query:
        """check that the player is registered for the active comp before adding info"""
        current_competition = Admin.objects.get(account_id=request.user.account_id).current_competition
        if current_competition == player.competition_id:
            data.append([str(player.player_id), str(player.first_name), str(player.last_name), str(player.date_of_birth), str(player.gender), str(player.county_id), str(player.availability)])
    t = Table(data)
    data_len = len(data)
    for each in range(data_len):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey
        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))
    aW = 540
    aH = 720
    w, h = header.wrap(aW, aH)
    header.drawOn(p, 72, aH)
    aH = aH - h
    w, h = t.wrap(aW, aH)
    t.drawOn(p, 72, aH-h)
    y = y + 100
    p.showPage()
    p.save()
    return response

"""
This view generates and downloads a CSV file containing the information for all
the players currently in the system.
"""
def report_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="current_comp_data.csv"'
    coachQuery = Coach.objects.all().order_by('last_name')
    heats = Heat.objects.all().order_by('heat_id')
    countyQuery = County.objects.all().order_by('name')
    playerQuery = Player.objects.all().order_by('last_name')
    p = csv.writer(response)
    p.writerow(["Athlete ID", "First Name","Last Name","Date of Birth","Gender","Club","Availability"])

    """info for all players"""
    for player in playerQuery:
        current_competition = Admin.objects.get(account_id=request.user.account_id).current_competition
        if current_competition == player.competition_id:
            p.writerow([str(player.player_id), str(player.first_name), str(player.last_name), str(player.date_of_birth), str(player.gender), str(player.county_id), str(player.availability)])

    p.writerow(["Coach Account", "First Name","Last Name","Email","Phone Number","county_id","Current Competition"])
    """info for all coaches"""
    for coach in coachQuery:
        if current_competition == coach.current_competition:
            p.writerow([str(coach.account), str(coach.first_name), str(coach.last_name), str(coach.email), str(coach.phone_number), str(coach.county_id), str(coach.current_competition)])

    p.writerow(["County ID", "County Name"])
    """info for all counties"""
    for county in countyQuery:
        p.writerow([str(county.county_id), str(county.name)])

    p.writerow(["Event ID", "Heat ID","Start Time"])
    """info for all events"""
    for heat in heats:
        if heat.event_id.competition_id == current_competition:
            p.writerow([str(heat.event_id), str(heat.heat_id), str(heat.start_time)])
            p.writerow(["Athlete First Name", "Last Name"])
            players = heat.players.all().order_by('last_name')
            """add name of each player in a heat"""
            for player in players:
                if player.competition_id == current_competition:
                    p.writerow([str(player.first_name), str(player.last_name)])
    return response

"""
This view generates and downloads a PDF file containing the information for all
the players currently in the system.
"""
def report_all_players(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_athletes.pdf"'
    query = Player.objects.all()
    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    p = canvas.Canvas(response)
    p.setTitle("All Athletes Report")
    header = Paragraph("All Athletes", style)
    y = 50
    data = [["Athlete ID", "First Name","Last Name","Date of Birth","Gender","Club","Availability"]]
    playerQuery = Player.objects.all().order_by('last_name')

    for player in playerQuery:
        current_competition = Admin.objects.get(account_id=request.user.account_id).current_competition
        if current_competition == player.competition_id:
            data.append([str(player.player_id), str(player.first_name), str(player.last_name), str(player.date_of_birth), str(player.gender), str(player.county_id), str(player.availability)])
    t = Table(data)
    data_len = len(data)
    for each in range(data_len):
        if each % 2 == 0:
            bg_color = colors.whitesmoke
        else:
            bg_color = colors.lightgrey
        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))
    aW = 540
    aH = 720
    w, h = header.wrap(aW, aH)
    header.drawOn(p, 72, aH)
    aH = aH - h
    w, h = t.wrap(aW, aH)
    t.drawOn(p, 72, aH-h)
    y = y + 100
    p.showPage()
    p.save()
    return response

"""
This view generates and downloads a PDF file containing the information for all
the counties currently in the system.
"""
def report_all_counties(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_clubs.pdf"'
    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    p = canvas.Canvas(response)
    p.setTitle("All Club Report")
    y = 50
    clubQuery = County.objects.all().order_by('name')
    data = [["Athlete ID", "First Name","Last Name","Date of Birth","Gender","Club","Availability"]]

    for club in clubQuery:
        current_competition = Admin.objects.get(account_id=request.user.account_id).current_competition
        header = Paragraph(str(club.name), style)
        query = Player.objects.filter(county_id=club.county_id).order_by('last_name')
        for player in query:
            if current_competition == player.competition_id:
                data.append([str(player.player_id), str(player.first_name), str(player.last_name), str(player.date_of_birth), str(player.gender), str(player.county_id), str(player.availability)])
        t = Table(data)
        data_len = len(data)
        for each in range(data_len):
            if each % 2 == 0:
                bg_color = colors.whitesmoke
            else:
                bg_color = colors.lightgrey
            t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))
        aW = 540
        aH = 720
        w, h = header.wrap(aW, aH)
        header.drawOn(p, 72, aH)
        aH = aH - h
        w, h = t.wrap(aW, aH)
        t.drawOn(p, 72, aH-h)
        y = y + 100
        p.showPage()
    p.save()
    return response

"""
This view generates and downloads a PDF file containing the information for all
the events currently in the system which have been used to create heats.
"""
def report_all_events(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_events.pdf"'
    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    p = canvas.Canvas(response)
    p.setTitle("All Events Report")
    query = Event.objects.all()
    heats = Heat.objects.all()

    """
    This section accesses the data from heats to present a list of all players currently
    scheduled for each heat.
    """

    for heat in heats:
        current_competition = Admin.objects.get(account_id=request.user.account_id).current_competition
        if heat.event_id.competition_id == current_competition:
            header = Paragraph(str(heat.event_id), style)
            subheader = Paragraph("Heat: "+str(heat.heat_id), style)
            timeheader = Paragraph("Start Time: " +str(heat.start_time), style)
            y = 50
            data = [["First Name", "Last Name"]]
            players = heat.players.all()

            for player in players:
                if player.competition_id == current_competition:
                    data.append([str(player.first_name), str(player.last_name)])
            t = Table(data)
            data_len = len(data)
            for each in range(data_len):
                if each % 2 == 0:
                    bg_color = colors.whitesmoke
                else:
                    bg_color = colors.lightgrey
                t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))
            aW = 540
            aH = 720
            w, h = header.wrap(aW, aH)
            header.drawOn(p, 72, aH)
            aH = aH - h
            w, h = subheader.wrap(aW, aH)
            subheader.drawOn(p, 72, aH-(1.1*h))
            aH = aH - (1.1*h)
            w, h = timeheader.wrap(aW, aH)
            timeheader.drawOn(p, 72, aH-(1.1*h))
            aH = aH - (1.1*h)
            w, h = t.wrap(aW, aH)
            t.drawOn(p, 72, aH-(1.1*h))
            y = y + 100
            p.showPage()
            data = [[]]

    p.save()
    return response

"""
This view generates and downloads a PDF file containing the information for a selected event currently in the system.
"""
def report_select_events(request):
    response = HttpResponse(content_type='application/pdf')
    event_selection = request.POST.getlist('event_id', None)
    response['Content-Disposition'] = 'attachment; filename=select_events.pdf'
    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    p = canvas.Canvas(response)
    p.setTitle('Select Events')

    """
    This section iterates through all selected events to access only the heat data associated
    with these events.
    """

    for i in range(len(event_selection)):
        if event_selection[i]!="":
            heats = Heat.objects.filter(event_id=event_selection[i])
            if len(heats) == 0:
                header = Paragraph("Schedule Not yet Made - Generate this report after creating schedule.", style)
                y = 50
                aW = 540
                aH = 720
                w, h = header.wrap(aW, aH)
                header.drawOn(p, 72, aH)
                p.showPage()

            for heat in heats:
                current_competition = Admin.objects.get(account_id=request.user.account_id).current_competition
                if heat.event_id.competition_id == current_competition:
                    header = Paragraph(str(heat.event_id), style)
                    subheader = Paragraph("Heat: "+str(heat.heat_id), style)
                    timeheader = Paragraph("Start Time: " +str(heat.start_time), style)
                    y = 50
                    data = [["First Name", "Last Name"]]
                    players = heat.players.all()
                    for player in players:
                        data.append([str(player.first_name), str(player.last_name)])
                    t = Table(data)
                    data_len = len(data)
                    for each in range(data_len):
                        if each % 2 == 0:
                            bg_color = colors.whitesmoke
                        else:
                            bg_color = colors.lightgrey
                        t.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))
                    aW = 540
                    aH = 720
                    w, h = header.wrap(aW, aH)
                    header.drawOn(p, 72, aH)
                    aH = aH - h
                    w, h = subheader.wrap(aW, aH)
                    subheader.drawOn(p, 72, aH-(1.1*h))
                    aH = aH - (1.1*h)
                    w, h = timeheader.wrap(aW, aH)
                    timeheader.drawOn(p, 72, aH-(1.1*h))
                    aH = aH - (1.1*h)
                    w, h = t.wrap(aW, aH)
                    t.drawOn(p, 72, aH-(1.1*h))
                    y = y + 100
                    p.showPage()
                    data = [[]]
    p.save()
    return response

"""
This view gathers information about all the coaches in the system, and renders
the view accessible from the Coaches tab of the admin dashboard.
"""
def admin_coaches(request):
    context = {
	'coach_list': Coach.objects.all(),
    }
    return HttpResponse(render(request,'admin_coaches.html',context))

"""
This view gathers information about all the counties in the system, and renders
the view accessible from the Counties tab of the admin dashboard.
"""
def admin_counties(request):
    return render(request, 'admin_counties.html', {'counties': County.objects.all()})

"""f
This view gathers information about all the events in the system, and renders
the view accessible from the Events tab of the admin dashboard.
"""
def admin_events(request):
    current_competition = Admin.objects.get(account_id = request.user.account_id).current_competition
    return render(request, 'admin_events.html', {'events': Event.objects.filter(competition_id=current_competition.competition_id)})

"""
This view gathers information about all the heats in the system, and renders
the view accessible from the Heats tab of the admin dashboard.
"""
def admin_heats(request):
    return render(request, 'admin_heats.html', {'heats': Heat.objects.all()})

"""
This view gathers information about all the competitions in the system, and renders
the view accessible from the Competitions tab of the admin dashboard.
"""
def admin_competitions(request):
    current_comp = Admin.objects.get(account_id=request.user.account_id).current_competition
    return render(request, 'admin_competitions.html', {'competitions': Competition.objects.all(), 'current_comp':current_comp})

"""
This view gathers information about all the admins in the system, and renders
the view accessible from the Admins tab of the admin dashboard.
"""
def admin_admins(request):
    return render(request,'admin_admins.html',{'administrators':Admin.objects.all()})

"""
This view renders and processes submissions to the form that allows admins to
create a coach record in the system.
"""
def admin_create_coach(request):
    # NEED TO TEST
    if request.method == 'POST':
        account_form = CustomUserCreationForm(request.POST)
        coach_form = CoachCreationForm(request.POST)
        if all((account_form.is_valid(),coach_form.is_valid())):
            account=account_form.save()
            coach=coach_form.save(commit=False)
            coach.account=account
            try:
                current_competition = Admin.objects.get(account_id = request.user.account_id).current_competition
                coach.current_competition = current_competition
            except:
                coach.current_competition = Competition.objects.get(name='new')
            coach.save()
            return redirect('admin_coaches')
    else:
        account_form = CustomUserCreationForm()
        coach_form = CoachCreationForm()
    return render(request, 'admin_create_coach.html', {'account_form': account_form, 'coach_form': coach_form})

"""
This view renders and processes submissions to the form that allows admins to
create a new admin account in the system.
"""
def admin_create_admin(request):
    #NEED TO TEST
    if request.method == 'POST':
        account_form = CustomUserCreationForm(request.POST)
        admin_form = AdminCreationForm(request.POST)
        if all((account_form.is_valid(),admin_form.is_valid())):
            account = account_form.save()
            admin = admin_form.save(commit=False)
            admin.account = account
            #added this try catch block to create a default current competition when we create our first admin
            try:
                #checks to see if we already have a current competition
                current_competition = Admin.objects.get(account_id = request.user.account_id).current_competition
                admin.current_competition = current_competition
            except:
                #if not, create one called default, and set it to the current. Admin can change this through the site later
                admin.current_competition = Competition.objects.create(name="default", start_date='2018-11-27')
            admin.save()
            return redirect('admin_admins')
    else:
        account_form = CustomUserCreationForm()
        admin_form = AdminCreationForm()
    return render(request, 'admin_create_admin.html', {'account_form': account_form, 'admin_form': admin_form})

"""
This view renders and processes submissions to the form that allows admins to
create an event record in the system.
"""
def admin_create_event(request):
    #NEED TO TEST
    if request.method == 'POST':
        form = EventCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_events')
    else:
        form = EventCreationForm()
    return render(request, 'admin_create_event.html', {'form': form})

"""
This view renders and processes submissions to the form that allows admins to
create a heat record in the system.
"""
def admin_create_heat(request):
    #NEED TO TEST
    if request.method == 'POST':
        form = HeatCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_heats')
    else:
        form = HeatCreationForm()
    return render(request, 'admin_create_heat.html', {'form': form})

"""
This view renders and processes submissions to the form that allows admins to
create a player record in the system.
"""
# WE NEED TO FIX THIS SO THAT ADMIN/COACHES CAN NOT SIGN UP PLAYERS FOR EVENTS THAT ARE NOT IN THE COMPETITION THEY ARE SIGNED UP FOR
def admin_create_player(request):
    #NEED TO TEST
    #pl = Player.objects.get(player_id = slug)
    #p_county = County.objects.get(county_id=1)

    p_event = Event.objects.all()

    form = AdminPlayerForm(request.POST or None)
    user = request.user.account_id
    try:
        competition = Admin.objects.get(account_id = user).current_competition
    except Admin.DoesNotExist:
        return HttpResponse("Please Login as Admin to Create Player")
    #form.county_id = p_county
    form.fields["competition_id"].initial = competition
    form.competition_id = competition
    template = "admin_create_player.html"
    context  = {
    "form":form,
    }
    if form.is_valid():
        obj = form.save(commit=False)
        obj.save()
        form.save_m2m()
        return redirect('admin_players')
    return render(request,template,context)

# WE NEED TO FIX THIS SO THAT ADMIN/COACHES CAN NOT SIGN UP PLAYERS FOR EVENTS THAT ARE NOT IN THE COMPETITION THEY ARE SIGNED UP FOR
def coach_create_player(request):
    #NEED TO TEST
    #pl = Player.objects.get(player_id = slug)
    #p_county = County.objects.get(county_id=1)
    p_event = Event.objects.all()
    coach = request.user.account_id
    form = CoachPlayerForm(request.POST or None)
    try:
        county = Coach.objects.get(account_id = coach).county_id
        competition = Coach.objects.get(account_id = coach).current_competition
    except Coach.DoesNotExist:
        county = None
        coach = None
        return HttpResponse("Please Login as Coach to Create Player")
    #form.fields["coach_id"].initial = coach
   # form.fields["county_id"].initial = county
   # form.county_id = county
    #form.fields["competition_id"].initial = competition
    #form.competition_id = competition
    template = "coach_create_player.html"
    context  = {
    "form":form,
    }

    if form.is_valid():
        form.instance.county_id = county
        form.instance.competition_id = competition
        obj = form.save(commit=False)
        #obj.county_id = county
        obj.save()
        form.save_m2m()
        return redirect('coach_players')
    return render(request,template,context)

"""
This view renders and processes submissions to the form that allows admins to
edit a coach record in the system.
"""
def admin_edit_coach(request,coach_id):
    #NEED TO TEST
    if request.method == 'POST':
        a=Coach.objects.get(account=Account.objects.get(pk=coach_id))
        account=a.account
        form = CoachCreationForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return redirect('admin_coaches')
    else:
        a=Coach.objects.get(account=Account.objects.get(pk=coach_id))
        account=a.account
        form = CoachCreationForm(instance=a)
    return render(request, 'admin_edit_coach.html', {'form': form, 'coach_id': coach_id, 'account':account})

"""
This view renders and processes submissions to the form that allows admins to
edit an event record in the system.
"""
def admin_edit_event(request,event_id):
    #NEED TO TEST
    if request.method == 'POST':
        a=Event.objects.get(pk=event_id)
        form = EventCreationForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return redirect('admin_events')
    else:
        a=Event.objects.get(pk=event_id)
        form = EventCreationForm(instance=a)
    return render(request, 'admin_edit_event.html', {'form': form, 'event_id': event_id})

"""
This view renders and processes submissions to the form that allows admins to
edit a heat record in the system.
"""
def admin_edit_heat(request,heat_id):
    if request.method == 'POST':
        a=Heat.objects.get(pk=heat_id)
        form = HeatCreationForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return redirect('admin_heats')
    else:
        a=Heat.objects.get(pk=heat_id)
        form = HeatCreationForm(instance=a)
    return render(request, 'admin_edit_heat.html', {'form': form, 'heat_id': heat_id})

"""
This view renders and processes submissions to the form that allows admins to
create a county record in the system.
"""
def admin_create_county(request):
    #NEED TO TEST
    if request.method == 'POST':
        form = CountyCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_counties')
    else:
        form = CountyCreationForm()
    return render(request, 'admin_create_county.html', {'form': form})

"""
This view renders and processes submissions to the form that allows admins to
edit a county record in the system.
"""
def admin_edit_county(request,county_id):
    #NEED TO TEST
    if request.method == 'POST':
        a=County.objects.get(pk=county_id)
        form = CountyCreationForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return redirect('admin_counties')
    else:
        a=County.objects.get(pk=county_id)
        form = CountyCreationForm(instance=a)
    return render(request, 'admin_edit_county.html', {'form': form, 'county_id': county_id})

"""
This view renders and processes submissions to the form that allows admins to
create a competition record in the system.
"""
def admin_create_competition(request):
    #NEED TO TEST
    if request.method == 'POST':
        form = CompetitionCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_competitions')
    else:
        form = CompetitionCreationForm()
    return render(request, 'admin_create_competition.html', {'form': form})

"""
This view renders and processes submissions to the form that allows admins to
create a competition from an existing competition in the system.
"""
#Imports all players and event information from existing competition to a new one
def admin_import_competition(request):
    #NEED TO TEST
    if request.method == 'POST':
        form = CompetitionImportForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['competition_name']
            start_date = form.cleaned_data['start_date']
            imported_competition = form.cleaned_data['imported_competition']
            new_competition = Competition.objects.create(name=name, start_date=start_date)
            new_comp_players = Player.objects.filter(competition_id=imported_competition)
            new_comp_events = Event.objects.filter(competition_id=imported_competition)
            #loop though all players and events from the selected competition and create them for the new competition
            for player in new_comp_players:
                Player.objects.create(first_name=player.first_name,last_name=player.last_name,date_of_birth=player.date_of_birth,gender=player.gender,availability=player.availability,county_id=player.county_id,competition_id=new_competition)
            for event in new_comp_events:
                Event.objects.create(name=event.name,relay_duration=event.relay_duration,athletes_per_relay=event.athletes_per_relay,competition_id=new_competition)
            return redirect('admin_competitions')
    else:
        form = CompetitionImportForm()
    return render(request, 'admin_import_competition.html', {'form': form})

"""
This view renders and processes submissions to the form that allows admins to
edit a competition record in the system.
"""
def admin_edit_competition(request,competition_id):
    #NEED TO TEST
    if request.method == 'POST':
        a=Competition.objects.get(pk=competition_id)
        form = CompetitionCreationForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            return redirect('admin_competitions')
    else:
        a=Competition.objects.get(pk=competition_id)
        form = CompetitionCreationForm(instance=a)
    return render(request, 'admin_edit_competition.html', {'form': form, 'competition_id': competition_id})

"""
This view gathers information about all the players in the system, and renders
the view accessible from the Players tab of the admin dashboard.
"""
def admin_dashboard(request):
    context = {
	'player_list': Player.objects.all(),
    }
    return HttpResponse(render(request,'admin_players.html',context))

"""
This view gathers information about all the players in the system, and renders
the view accessible from the Players tab of the admin dashboard.
"""
def admin_players(request):
    current_competition = Admin.objects.get(account_id=request.user.account_id).current_competition
    context = {
	'player_list': Player.objects.filter(competition_id=current_competition.competition_id),
    }
    return HttpResponse(render(request,'admin_players.html',context))

"""
This view gathers information about all the reports in the system, and renders
the view accessible from the Reports tab of the admin dashboard.
"""
def admin_reports(request):
    try:
        current_competition = Admin.objects.get(account_id=request.user.account_id).current_competition
    except:
        current_competition = Competition.objects.get()

    # if 'event_form' in request.POST:
    #     event_form = EventSelectionForm(request.POST)
    #     if event_form.is_valid():
    #         event_form.save()
    #         request.session.modified = True
    #         return redirect('report_select_events')
    # else:
    #     county_form = CountySelectionForm(request.POST)
    #     if county_form.is_valid():
    #         county_form.save()
    #         request.session.modified = True
    #         return redirect('report_select_county')
    county_form = CountySelectionForm()
    event_form = EventSelectionForm()
    context = {
    'county_form' : county_form,
    'event_form' : event_form,
    'event_list' : Event.objects.filter(competition_id = current_competition),
	'county_list' : County.objects.all()
    }

    return HttpResponse(render(request, 'admin_reports.html', context))

"""
This view gathers information about all the events and heats in the system, and renders
the view accessible from the Schedule tab of the admin dashboard.
"""
def admin_schedule(request):
    context = {
	'event_list': Event.objects.all(),
    }
    return HttpResponse(render(request,'admin_schedule.html',context))

"""
This view renders and processes submissions to the form that allows admins to
edit a player record in the system.
"""
def admin_edit_player(request,slug):
    #NEED TO TEST
    pl = Player.objects.get(player_id = slug)
    p_county = pl.county_id
    p_event = Event.objects.all()
    form = AdminPlayerForm(request.POST or None,initial = {'first_name':pl.first_name,'last_name':pl.last_name,'date_of_birth':pl.date_of_birth,'gender':pl.gender,'availability':pl.availability, 'county_id':p_county,  'events':p_event, 'competition_id':pl.competition_id})
    form.county_id = p_county
    template = "admin_edit_player.html"
    context  = {
    "form":form,
    }
    if form.is_valid():
        pl.first_name = form.cleaned_data['first_name']
        pl.last_name=form.cleaned_data['last_name']
        pl.date_of_birth=form.cleaned_data['date_of_birth']
        pl.gender = form.cleaned_data['gender']
        pl.availability = form.cleaned_data['availability']
        pl.events.set( form.cleaned_data['events'])
        pl.competition_id = form.cleaned_data['competition_id']
        pl.county_id = form.cleaned_data['county_id']
        #form.save_m2m()
        pl.save()
        return redirect('admin_players')
    return render(request,template,context)

"""
This view renders and processes submissions to the form that allows coaches to
edit a player record in the system.
"""
def coach_edit_player(request,slug):
    #NEED TO TEST
    pl = Player.objects.get(player_id = slug)
    #p_county = County.objects.get(county_id=1)
    p_event = Event.objects.all()
    form = CoachPlayerForm(request.POST or None,initial = {'first_name':pl.first_name,'last_name':pl.last_name,'date_of_birth':pl.date_of_birth,'gender':pl.gender,'availability':pl.availability,  'events':p_event})
    #coach = request.user.account_id
    #county = Coach.objects.get(account_id = coach)
    #county1 = county.account_id
    #form.fields["coach_id"].initial = coach
    #form.fields["county_id"].initial = county1
    template = "coach_edit_player.html"
    context  = {
    "form":form,
    }
    if form.is_valid():
        pl.first_name = form.cleaned_data['first_name']
        pl.last_name=form.cleaned_data['last_name']
        pl.date_of_birth=form.cleaned_data['date_of_birth']
        pl.gender = form.cleaned_data['gender']
        pl.availability = form.cleaned_data['availability']
        pl.events.set( form.cleaned_data['events'])
        #pl.coach_id=form.cleaned_data['coach_id']
		#form.save_m2m()
        pl.save()
        return redirect('coach_players')
    return render(request,template,context)

"""
This view renders and processes submissions to the form that allows admins to
delete a player record in the system.
"""
def ad_p_delete_function(request,p_id=None):
	object = Player.objects.get(player_id=p_id)
	object.delete()
	return redirect('admin_players')

"""
This view renders and processes submissions to the form that allows admins to
delete a county record in the system.
"""
def admin_delete_county(request,cy_id=None):
	object=County.objects.get(county_id=cy_id)
	object.delete()
	return redirect('admin_counties')

"""
This view renders and processes submissions to the form that allows admins to
delete a coach record in the system.
"""
def admin_delete_coach(request,coach_id=None):
	object=Coach.objects.get(account=Account.objects.get(pk=coach_id))
	object.delete()
	return redirect('admin_coaches')

"""
This view renders and processes submissions to the form that allows admins to
delete a event record in the system.
"""
def admin_delete_event(request,event_id):
	object=Event.objects.get(pk=event_id)
	object.delete()
	return redirect('admin_events')

"""
This view renders and processes submissions to the form that allows coaches to
delete a player record in the system.
"""
def co_p_delete_function(request,p_id=None):
	object = Player.objects.get(player_id=p_id)
	object.delete()
	return redirect('coach_players')

"""
This view renders and processes submissions to the form that allows admins to
delete a competition record in the system.
"""
def admin_delete_competition(request,competition_id):
	object=Competition.objects.get(pk=competition_id)
	object.delete()
	return redirect('admin_competitions')

"""
This view renders and processes submissions to the form that allows admins to
delete a heat record in the system.
"""
def admin_delete_heat(request,heat_id):
	object=Heat.objects.get(pk=heat_id)
	object.delete()
	return redirect('admin_heats')

def admin_set_current_competition(request,competition_id):
    for coach in Coach.objects.all():
        coach.current_competition = Competition.objects.get(pk=competition_id)
        coach.save()
    for admin in Admin.objects.all():
        admin.current_competition = Competition.objects.get(pk=competition_id)
        admin.save()
    return redirect('admin_competitions')

"""
This view renders and processes submissions to the form that allows coaches to
create a player record in the system.
"""
# def coachplayer(request):
#     p_county = County.objects.get(county_id=1)
#     p_event = Event.objects.all()
#     current_user = request.user
#     current_coach = Coach.objects.get(account=current_user)
#     #pl = Player.objects.all()
#     try:
#         pl = Player.objects.filter(coach_id = current_coach)
#     except:
#         pl = Player.objects.all()
#         pl = Player.objects.all()
# 	#later we'll need to only get the players that belong to the logged in coaches
#     template = "coach_dashboard.html"
# 	#login user's id = custom user's username
#     # form = CoachPlayerForm(request.POST or None,initial = { 'county_id':p_county, 'events':p_event, 'coach_id':current_coach})
#     context = {
#     "object_list":pl,
#     "form":form,
# 	#"form2":form2
#     }
# 	#form.player_id = '001'
# 	#form.availability='whenever'
#     form.county_id= p_county
# 	#if form2.is_valid():
# 		#right now we're just leaving these as placeholders
# 		#player and county_id are going to be automatically populated anyway.
# 		#form.cleaned_data['player_id'] = '001'
# 		#form.cleaned_data['availability'] = "whenever"
# 		#form.cleaned_data['county_id'] = '002'
# 		#form.events = form2.data
#     # if form.is_valid():
#     #     form.save()
# 	# 	#obj=form.save(commit=False)
# 	# 	#obj.save()
# 	# 	#form.save_m2m()
#     #     context ={
#     #     "object_list":pl,
#     #     "form":CoachPlayerForm(initial = {'county_id':p_county, 'events':p_event, 'coach_id':current_coach})
#     #     }
#     return render(request,template,context)

"""
This view gathers information about all the players visible by the logged in coach,
and renders the view accessible to the coaches from their dashboard.
"""
@login_required()
def coach_players(request):
    coach = request.user.account_id
    try:
        county = Coach.objects.get(account_id = coach).county_id
    except Coach.DoesNotExist:
        county = None
        coach = None
        return HttpResponse("Please Login as Coach")
    context = {
	'player_list': Player.objects.filter(county_id = county),
    }
    return HttpResponse(render(request,'coach_players.html',context))

"""
This view handles the login process, veryfying a user's credentials and redirecting
them to the appropriate dashboard.
"""
def login_view(request):
    #if form has been submitted
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if request.POST.get('remember-me', None):
            request.session.set_expiry(1209600)
        #Check if username/password combo is valid
        if form.is_valid():
            #find user and log them in
            user=form.get_user()
            login(request,user)
            #This is a placeholder, redirects to the blank page 'hello' until we have a good landing page
            if hasattr(user,'coach'):
                return redirect('coach_players')
            elif hasattr(user,'admin'):
                return redirect('admin_dashboard')
    else:
        #for a GET; this is when first loading the form
        form = AuthenticationForm()
    return HttpResponse(render(request, 'login.html',{'form':form}))

# """
# This view gathers information the currently logged in user and
# displays their account information.
# """
# def get_user_profile(request):
#         user = Account.objects.get(username=request.user.username)
#         return render(request, 'profile.html', {"user":user})

"""
This view gathers information the currently logged in admin user and
displays their account information.
"""
def admin_profile(request):
        user = Account.objects.get(username=request.user.username)
        try:
            #added this try catch block to make sure that the profile page doenst crash on initialization
            competition = Admin.objects.get(account_id=request.user.account_id).current_competition
        except:
            return render(request, 'admin_profile.html', {"user":user})
        return render(request, 'admin_profile.html', {"user":user,"competition":competition})

"""
This view gathers information the currently logged in coach user and
displays their account information.
"""
def coach_profile(request):
        user = Account.objects.get(username=request.user.username)
        return render(request, 'coach_profile.html', {"user":user})

"""
This view allows the admin to change any coach's password. While not the common practice, the customer does not
wish for coaches to change or reset their own passwords
"""
def admin_change_password(request, account_id):
    if request.method == 'POST':
        a = Account.objects.get(pk=account_id)
        password_form = PasswordChangeForm(request.POST, instance = a)
        if password_form.is_valid():
            password_form.save(commit=False)
            password=password_form.cleaned_data['password']
            a.set_password(password)
            a.save()
            return redirect('admin_coaches')
    else:
        a = Account.objects.get(pk=account_id)
        password_form = PasswordChangeForm(instance=a)
    return render(request, 'admin_change_password.html', {'password_form': password_form})

def logout_view(request):
    logout(request)
    return redirect('login')

"""
This is the file which contains the URL mappings we use in our application. Each view
has a URL that corresponds to it here, so that all views are accessible from their
dedicated URL.
"""

from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.urls import path
from . import views
from events.views import *

urlpatterns = [
	#report urls, which map to views that download the respective reports
	url(r'^report_all_players', report_all_players, name='report_all_athletes'),
	url(r'^report_csv', report_csv, name='report_csv'),
	url(r'^report_all_counties', report_all_counties, name='report_all_counties'),
	url(r'^report_select_county', report_select_county, name='report_select_county'),
	url(r'^report_all_events', report_all_events, name='report_all_events'),
	url(r'^report_select_events', report_select_events, name='report_select_events'),
	url(r'^report_player_schedule', report_player_schedule, name='report_player_schedule'),

	#the admin dashboard and the respective tabs in the interface
	url(r'^admin_dashboard/', admin_dashboard, name='admin_dashboard'),
	url(r'^admin_coaches/', admin_coaches, name='admin_coaches'),
	url(r'^admin_counties/', admin_counties, name='admin_counties'),
	url(r'^admin_events/', admin_events, name='admin_events'),
	url(r'^admin_heats/', admin_heats, name='admin_heats'),
	url(r'^admin_competitions/', admin_competitions, name='admin_competitions'),
	url(r'^refresh_schedule/', refresh_schedule, name='refresh_schedule'),
	url(r'^start_scheduler/', start_scheduler, name='start_scheduler'),

	#forms that allow the admin to create, edit and delete coaches
	url(r'^admin_create_coach/', admin_create_coach, name='admin_create_coach'),
	url(r'^admin_edit_coach/(?P<coach_id>\d+)/$', admin_edit_coach, name='admin_edit_coach'),
	url(r'^admin_delete_coach/(?P<coach_id>\d+)/$', admin_delete_coach, name='admin_delete_coach'),

	#forms that allow the admin to create, edit and delete counties
	url(r'^admin_create_county/', admin_create_county, name='admin_create_county'),
	url(r'^admin_edit_county/(?P<county_id>\d+)/$', admin_edit_county, name='admin_edit_county'),
	url(r'^admin_delete_county/(?P<cy_id>\d+)/$',admin_delete_county,name='admin_delete_county'),

	#forms that allow the admin to create, edit and delete events
	url(r'^admin_create_event/', admin_create_event, name='admin_create_event'),
	url(r'^admin_edit_event/(?P<event_id>\d+)/$', admin_edit_event, name='admin_edit_event'),
	url(r'^admin_delete_event/(?P<event_id>\d+)/$', admin_delete_event, name='admin_delete_event'),

	#forms that allow the admin to create, edit and delete heats
	url(r'^admin_create_heat/', admin_create_heat, name='admin_create_heat'),
	url(r'^admin_edit_heat/(?P<heat_id>\d+)/$', admin_edit_heat, name='admin_edit_heat'),
	url(r'^admin_delete_heat/(?P<heat_id>\d+)/$', admin_delete_heat, name='admin_delete_heat'),

	#forms that allow the admin to create, edit and delete competitions
	url(r'^admin_create_competition/', admin_create_competition, name='admin_create_competition'),
	url(r'^admin_import_competition/', admin_import_competition, name='admin_import_competition'),
	url(r'^admin_edit_competition/(?P<competition_id>\d+)/$', admin_edit_competition, name='admin_edit_competition'),
	url(r'^admin_delete_competition/(?P<competition_id>\d+)/$', admin_delete_competition, name='admin_delete_competition'),
	url(r'^admin_set_current_competition/(?P<competition_id>\d+)/$', admin_set_current_competition, name='admin_set_current_competition'),

	#forms that allow the admin to create, edit and delete players
	# url(r'^admin_player/', admin_player, name='admin_player'),
	url(r'^admin_create_player/', admin_create_player, name='admin_create_player'),
	url(r'^admin_edit_player/(?P<slug>[-\w]+)/$',views.admin_edit_player,name='admin_edit_player'),
	url(r'^admin_delete_player/(?P<p_id>[-\w]+)/$',ad_p_delete_function,name='ad_p_delete_function'),

	#a form that allows the admin to create another admin account
	url(r'^admin_admins/',admin_admins,name='admin_admins'),
	url(r'^admin_create_admin/', admin_create_admin, name='admin_create_admin'),

	#a form that allows the admin to change a password
	url(r'^admin_change_password/(?P<account_id>\d+)/$', admin_change_password, name='admin_change_password'),

	#more tabs in the admin dashboard
	url(r'^admin_players/', admin_players, name='admin_players'),
	url(r'^admin_reports/', admin_reports, name='admin_reports'),
	url(r'^admin_schedule/', admin_schedule, name='admin_schedule'),

	#the base url of the coach dashboard
	url(r'^coach_players/', coach_players, name='coach_players'),
	# url(r'^coach_players/', coachplayer, name='coach_players'),
	url(r'^coach_create_player/', coach_create_player, name='coach_create_player'),
	url(r'^coach_report/', coach_report, name='coach_report'),
	#url(r'^coachplayer/',views.coachplayer,name='coachplayer'),
	url(r'^coach_edit_player/(?P<slug>[-\w]+)/$',coach_edit_player,name='coach_edit_player'),
	url(r'^coach_delete/player/(?P<p_id>[-\w]+)/$',co_p_delete_function,name='co_p_delete_function'),
	#url(r'^coach_players/', coach_players, name='coach_players'),#

	#login and profile urls
	url(r'^login/', login_view, name='login'),
	url(r'^$', login_view, name='login'),
	#url(r'^profile/', get_user_profile, name='profile'),
	url(r'^admin_profile/', admin_profile, name='admin_profile'),
	url(r'^coach_profile/', coach_profile, name='coach_profile'),
	url(r'^logout/', logout_view, name='logout')
]

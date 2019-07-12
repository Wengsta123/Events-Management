/* schedule.c
 * C
 *
 * This is the main implementation file for the database scheduler
 * for the Events Management program for the 4-H Shooting education program competition.
 *
 * This section in particular reads arguments from the loader, then
 * opens the database, throws needed queries at it, and finally
 * runs the scheduling algorithm.
 *
 */

/* TODO
 *
 * Filter events & players by competition id
 * Get competitions
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "db_interface.h"
#include "scheduler_schedule.h"

#define DEFAULT_SQL_ENGINE	"sqlite3"

int line_count(const char * s);

int main(int argc, char * argv[]) {
	char database_name[256];
	char sql_engine[256];
	int testing;
	testing = 0;

	// initialize the database name to nothing
	database_name[0] = '\0';
	// initialize the sql_engine to the default
	strcpy(sql_engine, DEFAULT_SQL_ENGINE);

	int i, j; //counters
	/*	read command-line arguments	*/
	for (i = 1; i < argc; i++) {
		if (argv[i][0] == '-') {
			for (j = 1; argv[i][j]; j++) {
				switch (argv[i][j]) {
					case 'e': // engine
						if (argv[i][j+1]) {
							strcpy(sql_engine, argv[i] + j + 1);
						}
						else {
							i++;
							strcpy(sql_engine, argv[i]);
						}
					break;
					case 'd': // database
						if (argv[i][j+1]) {
							strcpy(database_name, argv[i] + j + 1);
						}
						else {
							i++;
							strcpy(database_name, argv[i]);
						}
					break;
					case 't': {
						testing = 1;
					}
					break;
				}
			}
		}
		else { // if no command-line switch, parse as the name of the database
			strcpy(database_name, argv[i]);
		}
	}

	/*	The following grabs data from the database	*/


	printf("%s::%d: getting data\n", __FILE__, __LINE__); // feedback

	db * database; // the database struct
	database = db_open(sql_engine, database_name);

	// TODO Competition getting
	// Have to get events_admin to get current competition

#define S_LEN 1048576 // 1MB
	char * s; //string buffer
	s = (char *)malloc(sizeof(*s)*S_LEN);
	// fire the first query at the database

	// if not in test mode, clear database of old heats and h.-player associations
	if (!testing) {
		printf("%s::%d: clearing database of old heats\n", __FILE__, __LINE__);
		db_query(database, "delete from events_heat;\ndelete from events_heat_players;\n", NULL, 0);
	}

	// get competition id from admin
	// (assumed consistent across all admins)
	printf("%s::%d: getting current competition ID\n", __FILE__, __LINE__);
	db_query(database, "select current_competition_id from events_admin;\n", s, S_LEN);
	for (i = 0; s[i]; i++) {
		if (!isdigit(s[i])) {
			s[i] = 0;
		}
	}
	// check if the database is (effectively) empty
	if (strlen(s) == 0) {
		fprintf(stderr, "error: database is empty...\nquiting...\n");
		return 0;
	}
	int current_competition_id; // current competition id
	current_competition_id = atoi(s); // parse it
	if (testing) // print the id if testing
		printf("%d\n", current_competition_id);

	// get current competition data
	printf("%s::%d: gathering competitions\n", __FILE__, __LINE__);
	char query_s[256];
	snprintf(query_s, 256, "select competition_id, name, start_date from events_competition where competition_id = %d;\n", current_competition_id);
	db_query(database, query_s, s, S_LEN);
	if (testing)
		printf("%s\n",s);
	int count;
	count = line_count(s);
	database->competition = (db_competition *)malloc(sizeof(*database->competition)*count);
	database->comp_count = count;
	if (!db_parse_events_competition(s, database->competition, database->comp_count)) {
		fprintf(stderr, "error: parsing returned database miss\n");
		fprintf(stderr, "%s\n", s);
		exit(1);
	}

	// get players
	printf("%s::%d: gathering athletes\n", __FILE__, __LINE__);
	snprintf(query_s, 256, "select player_id, first_name, last_name, date_of_birth, gender, availability, county_id_id, competition_id_id from events_player where competition_id_id = %d;\n", current_competition_id);
	db_query(database, query_s, s, S_LEN);
	if (testing)
		printf("%s\n", s);

	// count the number of players returned from the last query
	count = line_count(s);

	// create a space in memory for the players
	database->player = (db_player *)malloc(sizeof(*database->player) * count);
	database->player_count = count;

	// parse the query result into the player array
	if (!db_parse_events_player(s, database->player, database->player_count)) {
		fprintf(stderr, "error: parsing returned database miss\n");
		fprintf(stderr, "%s\n", s);
		exit(1);
	}

	// query parse the database for events
	printf("%s::%d: gathering events\n", __FILE__, __LINE__);
	snprintf(query_s, 256, "select event_id, name, relay_duration, athletes_per_relay, competition_id_id from events_event where competition_id_id = %d;\n", current_competition_id);
	db_query(database, query_s, s, S_LEN);
	if (testing)
		printf("%s\n", s);
	count = line_count(s);
	database->event_count = count;
	database->event = (db_event *)malloc(sizeof(*database->event) * count);
	if (!db_parse_events_event(s, database->event, database->event_count)) {
		fprintf(stderr, "error: parsing returned database miss\n");
		fprintf(stderr, "%s\n", s);
		exit(1);
	}

	// query and parse the database for player_events
	printf("%s::%d: gathering player events associations\n", __FILE__, __LINE__);
	db_query(database, "select id, player_id, event_id from events_player_events;\n", s, S_LEN);
	//printf("%s\n", s);
	count = line_count(s);
	database->pe_count = count;
	database->player_event = (db_player_event *)malloc(sizeof(*database->player_event) * count);
	if (!db_parse_events_player_events(s, database->player_event, database->pe_count)) {
		fprintf(stderr, "error: parsing returned database miss\n");
		fprintf(stderr, "%s\n", s);
		exit(1);
	}
	if (testing) {
		printf("%s\n", s);
	}


	/*	The following uses the scheduling algorithm described in scheduler_schedule.c	*/

	printf("%s::%d: scheduling...\n", __FILE__, __LINE__); // feedback

	// get the compeition start date
	time_t day_one; // time of the first day of the competition
	for (i = 0; i < database->comp_count; i++) {
		day_one = database->competition[i].start_date;
	}

	db_heat * heats; // array of generated heats
	db_heat_players * heat_players; // array of heat-player associations

	heats = schedule(database, day_one);
	heat_players = get_heat_players();

	/*	Export the schedule to the database	*/
	// The following creates SQL statements based on the calculated scheduler data

	size_t heat_s_len; // heat string length
	heat_s_len = 512;
	char heat_s[heat_s_len]; // heat string
	char heat_player_s[heat_s_len]; // heat-player string

	int final_query_len = 1<<10; // initial length of the final query string
	int final_query_cur_len = 0; // running length
	char * final_query; // final query string

	//initilize
	final_query =(char *)malloc(sizeof(*final_query) * final_query_len);
	*final_query = 0;

	// create SQL to for the heats themselves
	for (i = 0; heats[i].heat_id; i++) {
		// SQL format
		if (testing)
			printf("%s\n", ctime(&heats[i].start_time));
		snprintf(heat_s, heat_s_len,
				"INSERT INTO events_heat (\"heat_id\", \"start_time\",\"event_id_id\") VALUES (%d, datetime(%ld, 'unixepoch'), %d);\n",
				heats[i].heat_id,
				heats[i].start_time,
				//database->event[heats[i].event_id - 1].single_session_length_minutes,
				heats[i].event_id);

		// dynamic string reallocation
		if (final_query_cur_len + strlen(heat_s) > final_query_len) {
			char * keep;
			keep = final_query;
			final_query_len <<= 1;
			final_query = (char *)malloc(sizeof(*final_query) * final_query_len);
			strcpy(final_query, keep);
			free(keep);
		}
		strcat(final_query + final_query_cur_len, heat_s);
		final_query_cur_len += strlen(heat_s);
	}

	// similar to above, but for heat-player associations
	for (i = 0; heat_players[i].hp_id; i++) {
		//printf("%d %d %d\n", heat_players[i].hp_id,heat_players[i].heat_id,heat_players[i].player_id);
		snprintf(heat_player_s, heat_s_len,
				"INSERT INTO events_heat_players (\"id\", \"heat_id\", \"player_id\") values (%d, %d, %d);\n",
				heat_players[i].hp_id,
				heat_players[i].heat_id,
				heat_players[i].player_id);

		if (final_query_cur_len + strlen(heat_player_s) > final_query_len) {
			char * keep;
			keep = final_query;
			final_query_len <<= 1;
			final_query = (char *)malloc(sizeof(*final_query) * final_query_len);
			strcpy(final_query, keep);
			free(keep);
		}
		strcat(final_query + final_query_cur_len, heat_player_s);
		final_query_cur_len += strlen(heat_player_s);
	}

	//printf("%d\n", i);

	// print out the export string
	if (testing)
		printf("%s\n", final_query);
	// export to database
	if (!testing) {
		db_query(database, ".timeout 1000\n", NULL, 0);
		db_query(database, final_query, NULL, 0);
	}

	free(s);
	printf("%s::%d: success! closing...\n", __FILE__, __LINE__);
	db_close(database);

	return 0;
}

/* line_count(s)
 *
 * Counts the number of newline ('\n') characters in a string.
 *
 * s: The string
 *
 * Returns the count of newlines in string s
 */
int line_count(const char * s) {
	int i;
	int lines;

	lines = 0;
	for (i = 0; s[i]; i++) {
		if (s[i] == '\n') {
			lines++;
		}
	}
	
	return lines;
}

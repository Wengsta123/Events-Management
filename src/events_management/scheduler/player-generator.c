/* player-generator.c
 * C
 *
 * Louis Thomas (lat9nq)
 *
 * A small program to create hundreds of players in the database.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "db_interface.h"
#include "db_tables.h"
//#define	PLAYER_COUNT	400
int PLAYER_COUNT = 400;

int main(int argc, char * argv[]) {

	if (argc > 1) {
		PLAYER_COUNT = atoi(argv[1]);
	}

	db * database; // the databse
	db_event * events; // list of events
	char *s, // output string from database
	     *buf; // input database string
	int i, j, //counters
	    competition_id,
	    event_count;
	j = 0;

	// initialize buffers & database
	s = (char *)malloc(sizeof(*s)*1024);
	buf = (char *)malloc(sizeof(*buf)*1024);
	database = db_open("sqlite3", "../db.sqlite3");

	/*	GETTING DATA	*/

	// clear old players & events
	db_query(database, "DELETE FROM events_player;\n", NULL, 0);
	db_query(database, "DELETE FROM events_player_events;\n", NULL, 0);
	db_query(database, "SELECT current_competition_id FROM events_admin;\n", s, 1024);
	for (i = 0; s[i]; i++)
		if (s[i] == '\n')
			s[i] = '\0';
	competition_id = atoi(s);

	// get all the events
	sprintf(buf, "SELECT event_id, name, relay_duration, athletes_per_relay, competition_id_id FROM events_event WHERE competition_id_id == %d;\n", competition_id);
	db_query(database, buf, s, 1024);
	for (i = 0; s[i]; i++)
		if (s[i] == '\n')
			j++;
	event_count = j;
	events = (db_event *)malloc(sizeof(*events)*event_count);
	if (!db_parse_events_event(s, events, event_count)) {
		exit(0);
	}

	/*	CREATING PLAYERS	*/
	db_player * players; //player list
	db_player_event * pe; //player-event list
	int i_pe;
	i_pe = 0;
	players = (db_player *)malloc(sizeof(*players)*PLAYER_COUNT);
	pe = (db_player_event *)malloc(sizeof(*pe)*PLAYER_COUNT*event_count);

	srand(time(NULL));

	/*	GENERATE PLAYERS	*/
	for (i = 0; i < PLAYER_COUNT; i++) {
		players[i].player_id = i + 1;
		strcpy(players[i].first_name , "Athlete");
		snprintf(players[i].last_name, 100, "%d", i);
		players[i].dob = 1041397200;
		strcpy(players[i].gender, "Male");
		players[i].county_id = 1;

		j = rand();
		if (!(j & 7))
			strcpy(players[i].availability,"Saturday");
		else if (!((j+1) & 7))
			strcpy(players[i].availability,"Sunday");
		else
			strcpy(players[i].availability,"Both");

		u_int64_t player_event_count;
		player_event_count = (rand() | rand() | rand()) & (~(0xFFFFFFFFFFFFFFFF << event_count));

		// generate player-events
		for (j = 0; player_event_count && j < 64; j++) {
			if (!(player_event_count & 1))
				continue;
			printf("%d %d %d\n", i_pe, i + 1, events[j].event_id);
			player_event_count >>= 1;
			pe[i_pe].id = i_pe + 1;
			pe[i_pe].player_id = i + 1;
			pe[i_pe].event_id = events[j].event_id;
			i_pe ++;
		}
	}

	char * q;
	int q_len, q_size;
	q_len = 0;
	q_size = 256;
	q = (char *)malloc(sizeof(*q)*q_size);
	q[0] = 0;
	int buf_len;

	/*	FORMAT & INSERT INTO DATABASE	*/
	for (i = 0; i < PLAYER_COUNT; i++) {
		snprintf(buf, 1024, "INSERT INTO events_player (\"player_id\", \"first_name\", \"last_name\", \"date_of_birth\", \"gender\", \"availability\", \"competition_id_id\", \"county_id_id\") VALUES (%d, \"%s\", \"%s\", date(%ld, 'unixepoch'), \"%s\", \"%s\", %d, %d);\n",
				players[i].player_id,
				players[i].first_name,
				players[i].last_name,
				players[i].dob,
				players[i].gender,
				players[i].availability,
				competition_id,
				players[i].county_id);
		buf_len = strlen(buf);
		if  (q_len + buf_len > q_size) {
			q_size <<= 1;
			char * temp;
			temp = q;
			q = (char *)malloc(sizeof(*q)*q_size);
			if (!q) {
				exit(0);
			}
			strcpy(q, temp);
			free(temp);
		}
		strcat(q + q_len, buf);
		q_len += buf_len;
	}
	db_query(database, q, NULL, 0);

	q[0] = 0;
	q_len = 0;
	for (i = 0; i < i_pe; i++) {
		snprintf(buf, 1024, "INSERT INTO events_player_events (\"id\", \"player_id\", \"event_id\") VALUES (%d, %d, %d);\n",
				pe[i].id,
				pe[i].player_id,
				pe[i].event_id);
		buf_len = strlen(buf);
		if  (q_len + buf_len > q_size) {
			q_size <<= 1;
			char * temp;
			temp = q;
			q = (char *)malloc(sizeof(*q)*q_size);
			if (!q) {
				exit(0);
			}
			strcpy(q, temp);
			free(temp);
		}
		strcat(q + q_len, buf);
		q_len += buf_len;
	}
	db_query(database, q, NULL, 0);

	/*free(pe); //rip
	free(players);
	free(events);
	free(buf);
	free(s);*/
	db_close(database);

	return 0;
}

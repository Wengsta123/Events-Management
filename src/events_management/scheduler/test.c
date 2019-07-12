/* test.c
 * C
 *
 * This is a tester for the database scheduler.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include "scheduler_schedule.h"
#include "db_interface.h"

// prints something to stderr and exits the program
void err(char * arg) {
	fprintf(stderr, "Test failed: %s\n", arg);
	exit(0);
}

int main(int argc, char * argv[]) {
	int passed = 0; // number of tests passed

	/*	Test db_open	*/
	/* Tests if the created child returns a correct PID	*/

	char * db_engine = "sqlite3";
	char * db_name = "../db.sqlite3";
	db * database = db_open(db_engine, db_name);

	if (database->pid != 0) {
		passed ++;
	}
	else {
		err("Child should not be init");
	}

	/*	Test db_parse_int	*/
	/* Tests if it can read an int separated by a pipe	*/

	int res;
	db_parse_int(&res, "5|");
	if (res == 5)
		passed ++;
	else
		err("Int parser did not return 5");

	/* Tetss if it can read an int at the end of a line	*/

	db_parse_int(&res, "6\n");
	if (res == 6)
		passed++;
	else
		err("Int parser did not return 6");

	/*	Test db_parse_string	*/
	/* Tests if it can read a string separated by a pipe	*/

	char buf[256];
	db_parse_string(buf, "hello, world!|", 256);
	if (!strcmp(buf, "hello, world!")) {
		passed++;
	}
	else
		err("String returned was not \"hello, world!\"");

	/* Tests if it can parse to the end of a line	*/

	db_parse_string(buf, "hello, world!\n", 256);
	if (!strcmp(buf, "hello, world!")) {
		passed++;
	}
	else
		err("String returned was not \"hello, world!\"");

	/*	Test db_query	*/
	/* Tests if the database will read a query	*/

	char * query;
	query = "select * from NOT_A_TABLE;\n";
	db_query(database, query, buf, 256);

	if (!strcmp(buf,"")) 
		passed++;
	else
		err("Query output should be empty");

	db_close(database);
	database = db_open(db_engine, db_name);

	char buf_1024[1024];
	db_query(database, "SELECT * FROM events_heat_players;", buf_1024, 1024);
	printf("%s\n", buf_1024);

	/*	Test db_parse_events_player	*/

	int number_of_players = 2;
	db_player * players = (db_player *)malloc(sizeof(*players) * number_of_players);
	char * player_query = "1|Bob|Johnson|1/1/1967|Male|Both|1|1\n2|Abdeltawab|Hendawi|1/1/1991|Male|Saturday|1|1\n";
	db_parse_events_player(player_query,players,number_of_players);

	int parsing_error = 0;
	if (strcmp(players[1].first_name,"Abdeltawab"))
		parsing_error = 1;
	if (strcmp(players[1].last_name,"Hendawi"))
		parsing_error = 2;
	if (strcmp(players[1].gender,"Male"))
		parsing_error = 3;
	if (players[1].player_id != 2)
		parsing_error = 4;
	else
		passed++; // increment because testing the ID is itself a test of another bug
	if (parsing_error) {
		fprintf(stderr, "error %d\n", parsing_error);
		err("Parsing error during player parsing");
	}
	else
		passed++;

	/*	Test db_parse_events_event	*/

	int number_of_events = 2;
	db_event * events = (db_event*)malloc(sizeof(*events)*number_of_events);
	char * events_query = "1|Netflix and Chill|2|1|80\n2|Databases Final|40|1|180\n";
	db_parse_events_event(events_query, events, number_of_events);

	parsing_error = 0;
	if (strcmp(events[1].name, "Databases Final"))
		parsing_error = 1;
	if (events[1].event_id != 2)
		parsing_error = 2;
	else
		passed++; // increment because testing the ID is itself a test of another bug
	if (events[1].competitors_per_heat != 40)
		parsing_error = 3;
	if (parsing_error) {
		fprintf(stderr, "error %d\n", parsing_error);
		err("Parsing error during events parsing");
	}
	else
		passed++;


	/*	Test db_parse_events_player_event	*/

	int number_of_player_events = 2;
	db_player_event * pes = (db_player_event *)malloc(sizeof(*pes)*number_of_player_events);
	char * player_event_query = "1|1|1\n2|1|2\n";
	db_parse_events_player_events(player_event_query, pes, number_of_player_events);

	parsing_error = 0;
	if (pes[1].event_id != 2)
		parsing_error = 1;
	if (pes[1].id != 2)
		parsing_error = 2;
	else
		passed ++; // increment because testing the ID is itself a test of another bug
	if (pes[0].id != 1)
		parsing_error = 3;
	if (parsing_error) {
		fprintf(stderr, "error %d\n", parsing_error);
		err("Parsing error during player_events parsing");
	}
	else
		passed++;

	/*	Test db_parse_events_competition	*/
	int number_of_competitions;
	db_competition * comps;
	char * comp_query;

	parsing_error = 0;
	number_of_competitions = 2;
	comp_query = "1|2019|2019-08-31\n2|2018|2018-08-28\n";
	comps = (db_competition *)malloc(sizeof(*comps)*number_of_competitions);

	if (!db_parse_events_competition(comp_query, comps, number_of_competitions)) {
		fprintf(stderr, "error: parsing error: %s\n", comp_query);
	}
	else
		passed++;
	if (comps[0].competition_id != 1)
		parsing_error = 1;
	if (comps[1].competition_id != 2)
		parsing_error = 2;
	if (strcmp(comps[1].name, "2018"))
		parsing_error = 3;
	if (parsing_error) {
		fprintf(stderr, "error: error during competition parsing (%d)\n", parsing_error);
		exit(0);
	}
	else
		passed++;

	free(comps);


	// test query when we don't need any output
	db_query(database, "select * from nothing;", NULL, 0);
	passed++;


	/*	Test that the scheduler doesn't do nothing	*/

	db_heat * heats;
	database->player = players;
	database->event = events;
	database->player_event = pes;
	database->player_count = number_of_players;
	database->event_count = number_of_events;
	database->pe_count = number_of_player_events;
	heats = schedule(database, 0);

	if (heats == NULL)
		err("Scheduler should not return NULL");
	else
		passed++;
	if (heats[0].heat_id == 0)
		err("No heat should have NULL ID");
	else
		passed++;

	sc_heat_list * heat_list;
	heat_list = NULL;
	heat_list = sc_heat_list_insert(heat_list, &heats[0]);

	if (heat_list->next != NULL) {
		err("Heat list did not insert correctly\n");
	}
	else
		passed++;
	if (heat_list->heat != &heats[0]) {
		err("Heat list did not copy heat correctly\n");
	}
	else
		passed ++;

	/*	Heat Player association checking	*/

	db_heat_players * hp;
	hp = get_heat_players();
	if (hp[0].hp_id != 1) {
		err("Heat player ID should be 1\n");
	}
		passed++;
	// Test that the query engine works when not given a buffer
	// If it blocks, then we fail by default

	db_query(database, "select * from yes;", NULL, 0);
	passed++;

	printf("Tests passed: %d\ndone\n", passed);

	return 0;
}


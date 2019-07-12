/* scheduler_schedule.h
 * C Header
 *
 * This just lists the functions that will schedule the heats.
 * This file is necessary for collaborative work.
 *
 */
#ifndef SCHEUDLER_SCHEDULE_H
#define SCHEUDLER_SCHEDULE_H

#include "db_interface.h"

#define DEBUG	0

// Competition time parameters
// hopefully won't be constants in the future
#define SAT_START_TIME	9*60
#define SAT_END_TIME	(18*60 - 60)
#define SUN_START_TIME	8*60
#define SUN_END_TIME	13*60
#define INTERVAL	60
#define TIME_ZONE	5

typedef struct sc_heat_list_t { // linked list of heats
	db_heat * heat;
	struct sc_heat_list_t * next;
} sc_heat_list;

db_heat_players * hp;

// schedules the database
db_heat * schedule(db * database, const time_t day_one);
db_heat_players * get_heat_players();

sc_heat_list * sc_heat_list_insert(sc_heat_list * list, const db_heat * heat); // insert into a linked list
void sc_heat_list_free(sc_heat_list ** list, int length); // free an array of linked lists
int sc_player_event_lt(const void * a, const void * b); // compare a db_player_event to another

#endif

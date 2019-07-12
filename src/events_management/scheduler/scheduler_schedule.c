/* scheduler_schedule.c
 * C
 *
 * This is the implementation file for the actual algorithm that will create
 * and schedule the heats for the Events Management program.
 */
#include "scheduler_schedule.h"

//#define MAX_HEAT_COUNT	512
//int MAX_HEAT_COUNT	512;

int * events_per_player;
int MAX_HEAT_COUNT = 0;

/* schedule(database)
 *
 * Schedules a number of players, events, and those players' event selections
 * into a number of heats across two days.
 *
 * database: The database struct with data filled in from the SQLITE3 database
 *
 * On success, returns an array of heats.
 */
db_heat * schedule(db * database, const time_t day_one) {
	// The following variables are mirrors of the struct values
	int i,j; // counters
	int player_count;
	int event_count;
	int player_event_count;
	db_player ** player;
	db_event ** event;
	db_player_event * player_event;

	// Initialize the above variables
	player_count = database->player_count;
	event_count = database->event_count;
	player_event_count = database->pe_count;
	player = NULL;
	event = NULL;
	player_event = database->player_event;
	int max_event_id;
	int max_player_id;

	// create tables for player/event access
	max_event_id = 0;
	for (i = 0; i < event_count; i++) {
		if (database->event[i].event_id > max_event_id) {
			max_event_id = database->event[i].event_id;
		}
	}
	event = (db_event **)malloc(sizeof(*event)*max_event_id);
	memset(event, 0, sizeof(*event)*max_event_id);
	for (i = 0; i < event_count && i < max_event_id; i++) {
		event[database->event[i].event_id-1] = &database->event[i];
		// debug
		//printf("%d: %s\n", database->event[i].event_id-1, &database->event[i].name);
	}

	max_player_id = 0;
	for (i = 0; i < player_count; i++) {
		if (DEBUG)
			printf("%d\n", database->player[i].player_id);
		if (database->player[i].player_id > max_player_id) {
			max_player_id = database->player[i].player_id;
		}
	}
	player = (db_player **)malloc(sizeof(*player)*max_player_id);
	memset(player, 0, sizeof(*player)*max_player_id);
	for (i = 0; i < player_count && i < max_player_id; i++) {
		player[database->player[i].player_id - 1] = &database->player[i];
	}

	if (DEBUG)
		printf("max player count: %d\n", max_player_id);

	// Other variables
	db_heat * heat; // heat table
	int heats_needed; // count of heats needed by the scheduler
	int pid, eid; // player_id, event_id of the current player_event association
	sc_heat_list ** interval_list; // list of heat slots
	int heat_slots; // number of time slices available during the competition
	int sunday_slot; // the slot that begins on Sunday
	sc_heat_list *current_interval, // current slot pointed at
		     *interval_step; // interval stepped through in linked list

	// Initialize above variables (if necessary)
	heats_needed = 0;

	// calculate the number of slots we have for heats
	heat_slots = (SAT_END_TIME - SAT_START_TIME + SUN_END_TIME - SUN_START_TIME)/INTERVAL + 1;
	sunday_slot = (SAT_END_TIME - SAT_START_TIME)/INTERVAL;
	if (DEBUG)
		printf("heat slots: %d\tsunday slot: %d = %d\n", heat_slots, sunday_slot, sunday_slot*60 + SAT_START_TIME);
	heat = (db_heat*)calloc(sizeof(*heat)*heat_slots * event_count,1);
	MAX_HEAT_COUNT = heat_slots * event_count;
	// allocate a reflection on the number of heat slots available
	interval_list = (sc_heat_list **)malloc(sizeof(*interval_list)*heat_slots);
	memset(interval_list, 0,sizeof(*interval_list)*heat_slots);
	int player_interval[max_player_id][heat_slots]; // keep track of each players' schedule
	for (i = 0; i < max_player_id; i++)
		for (j = 0; j < heat_slots; j++)
			player_interval[i][j] = 0;

	// find players with most events, schedule those0
	events_per_player = (int *)malloc(sizeof(*events_per_player)*max_player_id);
	for (i = 0; i < max_player_id; i++) // initialize the array
		events_per_player[i] = 0;

	// count the number of events there are per player
	for (i = 0; i < player_event_count && i < max_player_id; i++) {
		pid = player_event[i].player_id;
		events_per_player[pid-1]++;
		if (player[pid-1] == NULL) { // ignore players from different competitions
			events_per_player[pid-1] -= 1000;
		}
	}

	// adjust sorting priorities as a result of day of availability
	for (i = 0; i < database->player_count; i ++) {
		if (!strcmp(database->player[i].availability, "Both")) {
			events_per_player[database->player[i].player_id - 1] -= 100;
			//printf("%d\n", database->player[i].player_id);
		}
	}

	// sort the list by the number of events_per_player
	qsort(player_event, player_event_count, sizeof(*player_event), &sc_player_event_lt);
	for (i = 0; DEBUG && i < player_event_count; i++) {
		printf("player %d has %d events planned\n", player_event[i].player_id, events_per_player[player_event[i].player_id]);
	}

	hp = (db_heat_players *)malloc(sizeof(*hp)*player_event_count);
	//printf("player_event_count: %d\n", player_event_count);
	int hp_i;
	hp_i = 0;
	j = 0;

	int unscheduled = 0;
//#define RAF
#ifdef	RAF
#define RAF_COUNT	16
	int raf_len = 16;
	void * raf[raf_len * RAF_COUNT];
	for (i = 0; i < raf_len; i++) {
		for (j = 0; j < RAF_COUNT; j++) {
			raf[i + j * RAF_COUNT] = calloc(1 << i, 1);
		}
	}
#endif
	// loop over the player_event associations
	for (i = 0; i < player_event_count; i++) {
#ifdef	RAF
		for (int k = 0; k < raf_len; k++) {
			for (int l = 0; l < RAF_COUNT; l++) {
				for (j = 0; j < (1 << k); j++) {
					if (*(u_int8_t *)(raf[k + RAF_COUNT * l] + j) != 0) {
						printf("error: fatal: array was modified\n");
						0/0;
					}
				}
				free(raf[k + l * RAF_COUNT]);
				raf[k + l * RAF_COUNT] = calloc((1<<k), 1);
			}
		}
		j = 0;
#endif
		if (j > heat_slots) {
			printf("error: fatal: j > allocation (%d)\n", j);
			exit(0);
		}
		if (heats_needed > event_count * heat_slots) { //MAX_HEAT_COUNT) {
			printf("error: fatal: more heats than allocated; line %d\n", __LINE__);
			*(u_int8_t *)(NULL) = 0;
			exit(0);
		}
		if (hp_i >= player_event_count) {
			printf("error: fatal: more heats than player-events\n");
			printf("\ti: %d, hp_i: %d, pec: %d\n", i, hp_i, player_event_count);
			exit(0);
		}
		int scheduled = 0;

		// Initialize variables
		pid = player_event[i].player_id;
		eid = player_event[i].event_id;
		if (DEBUG)
			printf("player_event id : %d, player %d, event %d\n", player_event[i].id, pid, eid); //debug

		if (player[pid-1] == NULL || pid > max_player_id)
			continue;
		if (event[eid-1] == NULL || eid > max_event_id)
			continue;

		int open_at; // keeps a time at which the player is able to compete at
		open_at = -1;
		int force_create;
		force_create = 0;

		// per each time slot
		for (j = 0; j < heat_slots; j++) {
			if (player[pid-1]->availability[1] == 'u' && j < sunday_slot) {
				j = sunday_slot;
			}
			int slot_time; // time of the day in minutes this slot is
			slot_time = SAT_START_TIME + j * INTERVAL;
			if (DEBUG)
				printf("trying slot %d... ", j);

			if (j + 1 >= heat_slots && player_interval[pid-1][j] && open_at > -1 && j < heat_slots) {
				j = open_at;
				force_create = 1;
				if (DEBUG)
					printf("forcing create heat on slot %d\n", j);
			}

			// if the player isn't busy at this time
			if (!player_interval[pid-1][j]) {
				if (DEBUG)
					printf("available at %d\n", slot_time);
				int found, // found a time
				    skip; // should skip the time slot
				found = skip = 0; // initialize

				// find out if the event is already taking place at this time
				interval_step = interval_list[j];
				while (interval_step != NULL) {
					//found++;
					if (DEBUG)
						printf("%08lx\n", (u_int64_t)interval_step);
					// if the heat has the correct event id
					if (interval_step->heat->event_id == eid) {
						found = 1; // we found the slot
						if (DEBUG)
							printf("found\n");
						// if the heat belongs to a different heat slot or there are no spaces available for the player
						if (interval_step->heat->start_time != slot_time
								|| interval_step->heat->player_count >= event[eid-1]->competitors_per_heat) {
							//printf("%s\n",player[pid-1]->availability);
							skip = 1; // keep looking
							if (DEBUG)
								printf("skipped...%d,%d (%d >= %d)\n",
										interval_step->heat->start_time != slot_time,
										interval_step->heat->player_count >= event[eid-1]->competitors_per_heat,
										interval_step->heat->player_count,
										event[eid-1]->competitors_per_heat);
						}
						break;
					}
					// step down the linked list
					interval_step = interval_step -> next;
				}
				// if the time slot contains a relevant heat
				if (found) {
					if (skip) {// if full or wrong time, skip
						if (DEBUG)
							printf("skipping..\n");
						found = -1;
					}
					else {
						// else, add the player to the heat
						current_interval = interval_step;
						current_interval->heat->player_count++;
						player_interval[pid-1][j] = 1;
						open_at = -1;
						hp[hp_i].hp_id = hp_i + 1;
						hp[hp_i].heat_id = current_interval->heat->heat_id;
						hp[hp_i].player_id = pid;
						scheduled = 1;
						if (DEBUG)
							printf("hp: id:%d, heat_id:%d, pid:%d\n", hp[hp_i].hp_id, hp[hp_i].heat_id, hp[hp_i].player_id);
						hp_i++;
						break;
					}
				}
				if (found < 1) { // no relevant heat at time
					if (open_at == -1 && found == 0) // set first available time if not already set
						open_at = j;
					// if reached end of all the heats
					if ((force_create || interval_list[j] == NULL || j + 1 >= heat_slots) && open_at >= 0) {
						// create the heat at the earliest available time for this player
						j = open_at;
						if (DEBUG)
							printf("created new heat\n");
						// allocate the heat and initialize it
						interval_list[j] = sc_heat_list_insert(interval_list[j], &heat[heats_needed]);
						current_interval = interval_list[j];
						heat[heats_needed].heat_id = heats_needed + 1;
						heat[heats_needed].start_time = SAT_START_TIME + j * INTERVAL;

						int duration; // duration of the event
						// get the event duration
						duration = event[eid-1]->single_session_length_minutes;
						heat[heats_needed].duration = duration;
						int k; // counter
						k = j;
						// set all overlapping time slots to busy
						// only happens when the duration is longer than the time interval
						while (duration > INTERVAL) {
							k++;
							if (k >= heat_slots)
								break;
							interval_list[k] = sc_heat_list_insert(interval_list[k], &heat[heats_needed]);
							player_interval[pid-1][k] = 1;
							duration -= INTERVAL;
						}
						// continue intializing
						heat[heats_needed].event_id = eid;
						heats_needed++;
						current_interval->heat->player_count++;
						player_interval[pid-1][j] = 1; // player is now busy at this time
						open_at = -1;
						hp[hp_i].hp_id = hp_i + 1;
						hp[hp_i].heat_id = heats_needed;
						hp[hp_i].player_id = pid;
						scheduled = 1;
						if (DEBUG)
							printf("hp: id:%d, heat_id:%d, pid:%d\n", hp[hp_i].hp_id, hp[hp_i].heat_id, hp[hp_i].player_id);
						hp_i++;
						break;
					}// if interval list[j] == NULL
				}
			}
		}
		if (!scheduled) {
			unscheduled++;
			if (open_at > -1)
				printf("\twarning: dropped a player-event (%d, %d)\n", unscheduled, open_at);
		}
	}

	if (unscheduled) {
		printf("warning: dropped (%d) player-events\n", unscheduled);
	}

	//printf("hp_i: %d\n", hp_i);
	hp[hp_i].hp_id = 0;

	/*	POST PROCESSING	*/

	// convert internal time to minutes since midnight of day one
	for (i = 0; i < heats_needed; i++) {
		if (heat[i].start_time >= 12*60)
			heat[i].start_time += 60;
		if (heat[i].start_time >= SAT_END_TIME)
			heat[i].start_time += SUN_START_TIME + 24*60 - SAT_END_TIME;
		if (heat[i].start_time >= 24*60 + 12*60)
			heat[i].start_time += 60;
		heat[i].start_time -= TIME_ZONE*60;
		heat[i].start_time *= 60;
		heat[i].start_time += day_one;
	}

	// collect garbage
	sc_heat_list_free(interval_list, heat_slots);
	free(interval_list);
	free(events_per_player);
	free(event);
	free(player);
	return heat;
}

// returns the heat-player associations
db_heat_players * get_heat_players() {
	return hp;
}

/* sc_heat_list_insert
 *
 * Inserts a sc_heat_list into a specified linked list of heats.
 * Inserts at the head of the list
 *
 * list : The list
 * heat : Pointer to the desired heat to point at
 *	Can be NULL
 *
 * Returns the new list pointer
 */
sc_heat_list * heat_list = NULL;
int heat_list_len = 0;
int heat_list_i = 0;
sc_heat_list * sc_heat_list_insert(sc_heat_list * list, const db_heat * heat) {
	if (heat_list_i > MAX_HEAT_COUNT) {
		printf("error: more heats than allocated\n");
		*(u_int8_t *)(NULL) = 0;
		exit(0);
	}
	if (!heat_list) {
		heat_list_len = MAX_HEAT_COUNT;
		heat_list = calloc(sizeof(*heat_list)*MAX_HEAT_COUNT,1);
	}
	//sc_heat_list * this = (sc_heat_list *)calloc(sizeof(*this), 1);
	sc_heat_list * this = &heat_list[heat_list_i];
	heat_list_i ++;
	this->next = list;
	this->heat = heat;
	return this;
}

/* sc_heat_list_free
 *
 * Interatively pops all of the nodes off of each entry in
 * a 2D linked list.
 * The list is an array of linked lists.
 *
 * list : The list
 * length : Length of the linked list
 */
void sc_heat_list_free(sc_heat_list ** list, int length) {

	free(heat_list);
	return;

	int i;
	sc_heat_list *step, *to_free;
	for (i = 0; i < length; i++) {
		step = list[i];
		while (step) {
			to_free = step;
			step = step->next;
			free(to_free);
		}
	}
}

/* sc_player_event_lt
 *
 * Comparison function for use with qsort in stdlib.h
 * Allows sorting of player_event entries
 * Sorts by putting players playing the most events at the front of the list,
 * then sorts by event id.
 *
 * Requires the global variable events_per_player to be initialized and ready with
 * the counts of events per each player.
 *
 * a : The first db_player_event entry
 * b : The second
 *
 * Returns -1 if higher priority,
 *	0 if equivalent priority, and
 *	1 if lower priority
 */
int sc_player_event_lt(const void * a, const void * b) {
	db_player_event *pe_a, *pe_b;
	int pid_a, pid_b;
	pe_a = (db_player_event *)a;
	pe_b = (db_player_event *)b;
	pid_a = pe_a->player_id;
	pid_b = pe_b->player_id;

	if (DEBUG)
		printf("[%d]: %d > [%d]: %d ? %d\n", pid_a, events_per_player[pid_a-1], pid_b, events_per_player[pid_b-1], events_per_player[pid_a-1] > events_per_player[pid_b-1]);
	if (events_per_player[pid_a-1] > events_per_player[pid_b-1]) {
		return -1;
	}
	else if (events_per_player[pid_a-1] == events_per_player[pid_b-1]) {
		if (pe_a->event_id < pe_b->event_id) {
			return -1;
		}
		else if (pe_a->event_id == pe_b->event_id) {
			return 0;
		}
	}

	return 1;
}


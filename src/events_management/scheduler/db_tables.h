/* db_tables.h
 * C Header
 *
 * This is a just a bunch of structs.
 * These structs match the description of the respective tables
 * in the Events Management program from the Sqlite3 database.
 */

#ifndef DB_TABLES_H
#define DB_TABLES_H

// events_player table
typedef struct db_player_t {
	int player_id; // Player id
	char first_name[100];
	char last_name[100];
	time_t dob; // date of birth
	char gender[16];
	int county_id; // foreign key to county table (not needed)
	int competition_id;
	char availability[9]; // availability of either day
} db_player;

// events_event
typedef struct db_event_t {
	int event_id; // id of the event
	char name[100];
	int competition_id; // unneeded foreign key
	int competitors_per_heat;
	int single_session_length_minutes;
} db_event;

// events_player_event
// In the database, this is a many-to-many relation of the above two tables
typedef struct db_player_event_t {
	int id;
	int player_id;
	int event_id;
} db_player_event;

// events_heat table
typedef struct db_heat_t {
	int heat_id; // id of the heat
	time_t start_time; // starting time of the heat
	int duration; // how long (in seconds) is the heat
	int event_id; // foreign key
	int player_count;
} db_heat;

// events_heat_players
typedef struct db_heat_players_t {
	int hp_id;
	int heat_id;
	int player_id;
} db_heat_players;

typedef struct db_competition_t {
	int competition_id;
	char name[100];
	time_t start_date;
} db_competition;

#endif


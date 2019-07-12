/* db_interface.h
 * C Header
 *
 * This is the header file for the interface to the sqlite3 database.
 * This was written with the purpose of reading from an Events Management program
 * for the 4-H shooting competition in Virginia.
 *
 * db_interface.c has better descriptions of the methods layed out here.
 */

#ifndef DB_INTERFACE_H
#define DB_INTERFACE_H

#define __need_timespec
#define _XOPEN_SOURCE
#include <time.h>

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <ctype.h>

#include <pthread.h>
#include <semaphore.h>
#include <errno.h>
#include <signal.h>

#include "db_tables.h"

// db_error error codes
typedef enum {
	DB_ERROR_NONE,
	DB_ERROR_TYPE
} db_error_t;

/* db_error
 *
 * The int is set at the beginning of each of the following functions,
 * defined by the above enumeration.
 */
db_error_t db_error;

// Argument struct for the worker thread
typedef struct db_worker_arg_t {
	char transfer; // transfer character read from the query
	int count; // count of characters read
	int pipe_in; // write pipe to the database
	int pipe_out; // read pipe from the database
	sem_t read_sem, sync_sem, red_sem, parent_sem; // asynchrony semaphores
	int post_red;
	pthread_t pthr; // pthread data
	pthread_attr_t attr; // pthread attribute data
	int terminate;
} db_worker_arg;

// Full database struct
typedef struct db_t {
	pid_t pid; // PID of the forked database child
	int in[2]; // input pipes of the database
	int out[2]; // output pipes of the database
	db_worker_arg worker; // the above struct in a pointable, parameter-passable form
	int player_count; // number of players read from the database
	db_player * player; // the events_player table
	int event_count; // the number of events from the database
	db_event * event; // the events_event tabl
	int pe_count; // the number of many-to-many associations between players and events
	db_player_event * player_event; // the many-to-many events_player_event table
	int comp_count;
	db_competition * competition;
	int queries; // how many queries have been performed
} db;

void * db_worker(void * arg); // worker thread
db * db_open(const char * db_engine, const char * db_name); // open the database
void db_query(db * database, const char * query, char * dest, int length); // sends and reads a query from the database
void db_close(db * database); // kill the database

int db_parse_int(int * dest, const char * s); // get an int from a query
int db_parse_string(char * dest, const char * s, int length); // get a string from the database
int db_parse_date(time_t * dest, const char * s, const char * frmt); // get a date from the database

int db_parse_events_player(char * query_result, db_player * dest, int count); // reads a events_player table from a query
int db_parse_events_event(char * query_result, db_event * dest, int count);
int db_parse_events_player_events(char * query_result, db_player_event * dest, int count);
int db_parse_events_competition(char * query_reult, db_competition * dest, int count);

#endif



/* db_interface.c
 * C
 *
 * Louis Thomas
 * Events Management
 *
 * This is the implementation file for the Sqlite3 database interface.
 */
#include "db_interface.h"

/* void * db_worker(arg)
 *
 * This is a pthread worker method.
 * It reads data from the database character-by-character.
 * We need this in an asynchronous thread because I want to give the database multiple queries one at a time,
 * and if it blocks on the read() system call, it won't block the entire program.

 * Takes a &db_worker_arg as an argument.
 * Returns NULL
 */
void * db_worker(void * arg) {
	db_worker_arg * args; // argument struct
	char c; // character buffer
	int count; // count of read characters

	args = (db_worker_arg *)arg;
	args->terminate = 0;
	c = 0;
	args->post_red = 1;
	// the following loop is tightly synced with the db_query method
	// currently only works for a single query
	while (1) {
		//printf("1"); // debug
		sem_wait(&args->parent_sem); // wait for the master to kick off the run
		//printf("2"); //debug
		sem_post(&args->read_sem); // let the master know that we are ready to read
		//printf("3"); //debug
		count = read(args->pipe_out,&c,1); // read
		if (args->terminate) {
			break;
		}
		//printf("4"); //debug
		args->transfer = c; // place the new character in the argument struct for communication
		args->count = count;
		if (args->post_red) {
			sem_post(&args->red_sem); // let the master know that we did not block on reading the database
		}
		args->post_red = 1;
		sem_post(&args->sync_sem); // let the master know that the communication is ready to read
		//printf("5\n"); //debug
	}

	return NULL;
}

/* db * db_open(db_engine, db_name)
 *
 * Opens the database in a forked child process, then kicks off the slave thread so that
 * the program is ready to take queries to the database.
 *
 * db_engine: The name of the database program (i.e. sqlite3, postgres, etc.)
 * db_name: 
 */
db * db_open(const char * db_engine, const char *db_name) {
	db_error = DB_ERROR_NONE; // initialize to no error

	db * res; // result database struct
	db_worker_arg * worker; // refrence the slave database reader struct
	pid_t child; // forked child

	res = (db *)malloc(sizeof(*res));
	worker = &res->worker;

	// create the data pipes to talk to the child
	if (pipe(res->in) < 0) {
		int err = errno;
		fprintf(stderr,"error (%d): pipe creation failed\n", err);
		exit(0);
	}
	if (pipe(res->out) < 0) {
		int err = errno;
		fprintf(stderr,"error (%d): pipe creation failed\n", err);
		exit(0);
	}

	child = fork();
	if (child < 0) {
		int err = errno;
		fprintf(stderr,"error (%d): child creation failed\n", err);
		exit(0);
	}
	else if (!child) { // if the current instance is the child

		/* 	CHILD CODE	*/

		dup2(res->in[0], STDIN_FILENO); // dup the pipes into our STDIN/OUT
		dup2(res->out[1], STDOUT_FILENO);

		// close unneeded pipes
		close(res->out[0]);
		close(res->out[1]);
		close(res->in[0]);
		close(res->in[1]);

		// execute the database program
		execlp(db_engine, db_engine, db_name, NULL);

		// we only get here if the database failed to execute
		fprintf(stderr, "error: failed to execute %s\n", db_engine);
		exit(0);
	}

	/*	PARENT CODE	*/

	// remember the child PID
	res->pid = child;
	// close unneeded pipes
	close(res->in[0]);
	close(res->out[1]);

	// initialize semaphores for the slave thread
	sem_init(&worker->read_sem, 0, 0);
	sem_init(&worker->red_sem, 0, 0);
	sem_init(&worker->sync_sem, 0, 0);
	sem_init(&worker->parent_sem, 0, 0);

	// kick off the slave thread
	pthread_attr_init(&worker->attr);
	pthread_create(&worker->pthr, &worker->attr, &db_worker, (void *)worker);

	// initialize the slave's focused pipes
	worker->pipe_out = res->out[0];
	worker->pipe_in = res->in[1];

	res->queries = 0;

	return res;
}


void db_close(db * database) {
	//kill(database->pid, 15);
	database->worker.terminate = 1;
	char * tables = "tables\n\0";
	if (write(database->worker.pipe_in, tables, strlen(tables)) < strlen(tables)) {
		int err = errno;
		fprintf(stderr, "error (%d): couldn't write message to child buffer\n", err);
		exit(0);
	}

	close(database->in[1]);
	close(database->out[0]);
}

/* db_query(database, query, dest, length)
 *
 * Sends a string to the database, and writes a resulting string into dest.
 *
 * database: The database struct, opened by db_open
 * query: The query to send to the database
 * dest: The destination string to write the database result
 * length: The maximum length provided by the dest string
 */
void db_query(db * database, const char * query, char * dest, int length) {
	db_error = DB_ERROR_NONE; // reset the db_error integer

	int add_sec; // seconds to wait for the query to block
	int i; // counter
	struct timespec ts; // delay for the semaphore
	db_worker_arg * worker; // pointer to the worker struct

	worker = &database->worker;
	add_sec = 1;
	ts.tv_nsec = 0;

	// send the query to the database
	if (write(worker->pipe_in, query, strlen(query)) < strlen(query)) {
		int err = errno;
		fprintf(stderr, "error (%d): could not write full query to database\n", err);
		exit(0);
	}

	if (dest == NULL)
		return;

	i = 0;
	dest[i] = 0;
	// read from the worker thread
	if (database->queries) {
		sleep(1);
		dest[i] = worker->transfer;
		i += worker->count;
		dest[i] = 0;
	}

	// let the worker thread start
	sem_post(&worker->parent_sem);
	while (1) {
		sem_wait(&worker->read_sem);
		//printf("1"); //debug
		//fflush(stdout);
		ts.tv_sec = time(NULL) + add_sec;
		sem_timedwait(&worker->red_sem, &ts);
		if (errno == ETIMEDOUT) {
			worker->post_red = 0;
			errno = 0;
			break;
		}
		//printf("2"); //debug
		//fflush(stdout);
		sem_wait(&worker->sync_sem);
		dest[i] = worker->transfer;
		i += worker->count;
		dest[i] = 0;

		if (i >= length) {
			break;
		}
		sem_post(&worker->parent_sem);
	}

	sem_destroy(&worker->red_sem);
	sem_init(&worker->red_sem, 0,0);

	database->queries ++;
}

/* db_parse_int(dest, s)
 *
 * Read an int from a string
 * Good for sqlite3 database query strings
 *
 * dest: where readout is going
 * s: the query string result
 *
 * Returns the number of characters read to return the int
 */
int db_parse_int(int * dest, const char * s) {
	db_error = DB_ERROR_NONE;
	int i; // counter
	char buf[256]; // buffer string (256 characters is a long number)
	for (i = 0; i < 256 && s[i]; i++) { // loop until either the buffer is filled or the string has ended
		buf[i] = 0; // the current character is the null terminator
		if (s[i] == '|' || isspace(s[i])) { // if the pipe separator or end of int
			break; // stop
		}
		if (!isdigit(s[i])) { // if not number
			db_error = DB_ERROR_TYPE; // there is an error in the parsing
			return 0;
		}
		// set the buffer to the currently pointed to character
		buf[i] = s[i];
	}

	// convert the buffer to an int
	*dest = atoi(buf);
	return i + 1;
}

/* db_parse_string(dest, s, length)
 *
 * Find and copy out the string from the database query.
 * Stops on either a newline or a pipe separator.
 * Good for sqlite3 queries
 *
 * dest: The spot in memory to place the string
 * s: The database query result
 * length: The max length for the destination string
 *
 * On success, returns the number of characters read.
 */
int db_parse_string(char * dest, const char * s, int length) {
	db_error = DB_ERROR_NONE;

	int i; //counter
	for (i = 0; i < length && s[i]; i++) { // loop for the length of either string (shortest first)
		dest[i] = 0;
		if (s[i] == '|' || s[i] == '\n') { // if pipe or newline
			break; // stop
		}
		dest[i] = s[i]; // copy into the destination
	}
	return i + 1;
}

/* db_parse_date(dest, s, frmt)
 *
 * Turns a time string into the number of seconds since the Unix epoch.
 * Stops on pipe or newline
 * Good for sqlite3 query strings.
 *
 * dest: The spot in memory for the result
 * s: The string from the query
 * frmt: The date string, described in the man pages for date
 *
 * On success, returns the number of characters read from string s
 */
int db_parse_date(time_t * dest, const char * s, const char * frmt) {
	db_error = DB_ERROR_NONE;
	int i;
	for (i = 0; s[i]; i++) {
		if (s[i] == '|' || s[i] == '\n') {
			break;
		}
	}

	struct tm this_date;
	memset(&this_date, 0, sizeof(this_date));
	char s_buf[256];

	strncpy(s_buf,s,i);
	s_buf[i] = 0;
	strptime(s_buf, frmt, &this_date);

	*dest = mktime(&this_date);
	return i + 1;
}

/* db_parse_events_player(query_result, dest, count)
 *
 * Reads an entire query from the database and synthesizes it into a db_player struct table.
 *
 * query_result: The string returned from the query
 * dest: The array in memory to place the data
 * count: The number of db_players at array dest
 */
int db_parse_events_player(char * query_result, db_player * dest, int count) {
	int i;
	int j;
	for (i = j = 0; query_result[i] && j < count; i++) {
		if (query_result[i] == '\n') {
			return 0;
		}
		//printf("%s\n", query_result+i);
		i += db_parse_int(&dest[j].player_id,query_result + i);
		i += db_parse_string(dest[j].first_name,query_result + i,100);
		i += db_parse_string(dest[j].last_name,query_result + i,100);
		i += db_parse_date(&dest[j].dob,query_result + i,"%Y-%m-%d");
		i += db_parse_string(dest[j].gender,query_result + i,16);
		i += db_parse_string(dest[j].availability,query_result + i,9);
		i += db_parse_int(&dest[j].county_id,query_result + i);
		i += db_parse_int(&dest[j].competition_id,query_result + i);
		i -= 1;
		if (query_result[i] != '\n') {
			return 0;
		}
		j++;
	}
	return 1;
}

/* db_parse_events_event
 *
 * Reads a whole query and returns the events in a db_event struct array.
 *
 * query_result: The string returned from the query
 * dest: The array in memory to place the data
 * count: The number of db_events at array dest
 */
int db_parse_events_event(char * query_result, db_event * dest, int count) {
	int i, j;
	for (i = j = 0; query_result[i] && j < count; i++) {
		if (query_result[i] == '\n') {
			return 0;
		}
		//printf("%s\n", query_result + i);
		i += db_parse_int(&dest[j].event_id, query_result + i);
		i += db_parse_string(dest[j].name, query_result + i,100);
		i += db_parse_int(&dest[j].single_session_length_minutes, query_result + i);
		i += db_parse_int(&dest[j].competitors_per_heat, query_result + i);
		i += db_parse_int(&dest[j].competition_id, query_result + i);
		i -= 1;
		if (query_result[i] != '\n') {
			return 0;
		}
		j++;
	}
	return 1;
}

/* db_parse_events_event
 *
 * Reads a whole query and returns the player_events associations in a db_player_event struct array.
 *
 * query_result: The string returned from the query
 * dest: The array in memory to place the data
 * count: The number of db_player_events at array dest
 *
 * Returns 1 if no error detected
 * Returns 0 if there was a parsing error
 */
int db_parse_events_player_events(char * query_result, db_player_event * dest, int count) {
	int i, j;
	for (i = j = 0; query_result[i] && j < count; i++) {
		if (query_result[i] == '\n') {
			return 0;
		}
		i += db_parse_int(&dest[j].id, query_result + i);
		i += db_parse_int(&dest[j].player_id, query_result + i);
		i += db_parse_int(&dest[j].event_id, query_result + i);
		i -= 1;
		if (query_result[i] != '\n') {
			return 0;
		}
		j++;
	}
	return 1;
}

/* db_parse_events_competition
 *
 * Reads a whole query and returns the competition fields in a db_competition struct array.
 *
 * query_result: The string returned from the query
 * dest: The array in memory to place the data
 * count: The number of db_player_events at array dest
 *
 * Returns 1 if no error detected
 * Returns 0 if there was a parsing error
 */
int db_parse_events_competition(char * query_result, db_competition * dest, int count) {
	int i, j;
	for (i = j = 0; query_result[i] && j < count; i++) {
		if (query_result[i] == '\n') {
			return 0;
		}
		i += db_parse_int(&dest[j].competition_id, query_result + i);
		i += db_parse_string(dest[j].name, query_result + i, 100);
		i += db_parse_date(&dest[j].start_date, query_result + i, "%Y-%m-%d");
		i -= 1;
		if (query_result[i] != '\n') {
			return 0;
		}
		j++;
	}
	return 1;
}


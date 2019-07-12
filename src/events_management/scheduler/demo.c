#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <string.h>

#include <pthread.h>
#include <semaphore.h>
#include <errno.h>
#include <time.h>

#define LS	"ls"

sem_t sem, sync_sem, read_sem, red_sem;

typedef struct worker_args_t {
	int out;
	int count;
	char t;
} worker_args;

void * worker(void * arg_t) {
	worker_args * args;
	args = (worker_args *)arg_t;

	char c;
	int count = 0;
	c = 0;
	while (1) {
		sem_wait(&sem);

		sem_post(&read_sem);
		count = read(args->out, &c, 1);
		sem_post(&red_sem);
		args->count = count;
		args->t = c;
		sem_post(&sync_sem);
		if (count == 0) {
			break;
		}
	}

	return NULL;
}

int main(int argc, char * argv[]) {

	int in[2];
	int out[2];

	pipe(in);
	pipe(out);

	int pid = fork();
	if (pid == 0) {
		dup2(in[0], STDIN_FILENO);
		dup2(out[1], STDOUT_FILENO);

		close(in[0]);
		close(out[1]);
		close(in[1]);
		close(out[0]);

#define SQLITE "sqlite3"
		//execlp("ls", "ls", NULL);
		//execlp("bc", "bc", NULL);
		execlp(SQLITE, SQLITE, "../db.sqlite3", NULL);
		exit(0);
	}

	close(in[0]);
	close(out[1]);

	pthread_attr_t attr;
	pthread_t pthr;
	worker_args args;
	args.out = out[0];

	sem_init(&sem, 1, 0);
	sem_init(&sync_sem, 1, 0);
	sem_init(&read_sem, 1, 0);
	sem_init(&red_sem, 1, 0);

	pthread_attr_init(&attr);
	pthread_create(&pthr, &attr, &worker, (void *)&args);

	char s[256];
	int i, j, exited;
	for (i = 0; i < 256; i++){
		s[i] = 0;
	}
#define QUERY	"select * from events_county;\n"
//#define QUERY	"1+1"
	write(in[1], QUERY, strlen(QUERY));
	printf("%s\n", QUERY);
	//close(in[1]);
	sem_post(&sem);

	i = 0;
	j = 0;
	exited = 0;

	struct timespec wait_amount;

	int add_time = 1;
	wait_amount.tv_nsec = 0;

	while (1) {
		sem_wait(&read_sem);
		wait_amount.tv_sec = time(NULL) + add_time;
		sem_timedwait(&red_sem, &wait_amount);
		if (errno == ETIMEDOUT) {
			break;
		}
		sem_wait(&sync_sem);
		write(STDOUT_FILENO,&args.t,1);
		fflush(stdout);
		sem_post(&sem);
	}

	return 0;
}

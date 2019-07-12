CC=gcc
CCFLAGS=-Wall -O2 -std=c99
#-fprofile-arcs -ftest-coverage
LIBS=-lpthread

%.o:%.c
	$(CC) $(CCFLAGS) -c -o$@ $<

all:
	+make scheduler
	+make player-generator

SCHEDULER_OFILES=scheduler.o db_interface.o scheduler_schedule.o
scheduler:$(SCHEDULER_OFILES)
	$(CC) $(CCFLAGS) -o$@ $(SCHEDULER_OFILES) $(LIBS)

TEST_OFILES=test.o db_interface.o scheduler_schedule.o
test:$(TEST_OFILES)
	$(CC) $(CCFLAGS) -o$@ $(TEST_OFILES) $(LIBS)

PG_OFILES=player-generator.o db_interface.o
player-generator:$(PG_OFILES)
	$(CC) $(CCFLAGS) -o$@ $^ $(LIBS)

.PHONY:clean
clean:
	-rm -vf *.o player-generator scheduler test *.gcno *.gcda *.gcov

db_interface.o: db_interface.c db_interface.h db_tables.h
demo.o: demo.c
player-generator.o: player-generator.c db_interface.h db_tables.h
scheduler.o: scheduler.c db_interface.h db_tables.h scheduler_schedule.h
scheduler_schedule.o: scheduler_schedule.c scheduler_schedule.h \
 db_interface.h db_tables.h
test.o: test.c scheduler_schedule.h db_interface.h db_tables.h

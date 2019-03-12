all: database

include ../pip_list.mk

database: piplist

pushdb:
	true

run: database
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: all clean run database pushdb

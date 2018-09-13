# for now hammering on just picorv32
# consider instead aggregating multiple projects
PRJ?=picorv32
PRJN?=8

all: build/tilea.json

clean:
	rm -rf build
	cd speed && $(MAKE) clean
	cd timgrid && $(MAKE) clean
	cd projects && $(MAKE) clean

speed/build/speed.json:
	cd speed && $(MAKE)

timgrid/build/timgrid.json:
	cd timgrid && $(MAKE)

build/tilea.json: projects/$(PRJ)/build/tilea.json
	mkdir -p build
	cp projects/$(PRJ)/build/tilea.json build/tilea.json

projects/$(PRJ)/build/tilea.json: speed/build/speed.json timgrid/build/timgrid.json
	cd projects/$(PRJ) && $(MAKE) N=$(PRJN)


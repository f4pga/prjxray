# for now hammering on just picorv32
# consider instead aggregating multiple projects
PRJ?=oneblinkw
PRJN?=1

all: build/timgrid-v.json bel/build/sdf

clean:
	rm -rf build
	cd speed && $(MAKE) clean
	cd timgrid && $(MAKE) clean
	cd bel && $(MAKE) clean
	cd projects/$(PRJ) && $(MAKE) clean

bel/build/sdf:
	cd bel && $(MAKE)

speed/build/speed.json:
	cd speed && $(MAKE)

timgrid/build/timgrid.json:
	cd timgrid && $(MAKE)

build/timgrid-v.json: projects/$(PRJ)/build/timgrid-v.json
	mkdir -p build
	cp projects/$(PRJ)/build/timgrid-v.json build/timgrid-v.json

projects/$(PRJ)/build/timgrid-v.json: speed/build/speed.json timgrid/build/timgrid.json
	cd projects/$(PRJ) && $(MAKE) N=$(PRJN)


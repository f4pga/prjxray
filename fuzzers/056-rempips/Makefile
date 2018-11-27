# WARNING: N cannot be reduced or -m will always fail
N := 10
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 5 -M 15 -o build/seg_int_l.db $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o build/seg_int_r.db $(addsuffix /segdata_int_r.txt,$(SPECIMENS))

pushdb:
	${XRAY_DBFIXUP} --db-root . --clb-int
	${XRAY_MERGEDB} int_l build/seg_int_l.db
	${XRAY_MERGEDB} int_r build/seg_int_r.db

$(SPECIMENS_OK): build/todo.txt
	mkdir -p build
	bash ${XRAY_DIR}/utils/top_generate.sh $(subst /OK,,$@)
	touch $@

build/pips_int_l.txt: piplist.tcl
	mkdir -p build
	cd build && vivado -mode batch -source ../piplist.tcl

# Used 1) to see if we are done 2) pips to try in generate.tcl
build/todo.txt: build/pips_int_l.txt
	#python3 maketodo.py --no-strict | sort -R | head -n10 > build/todo.txt.tmp
	python3 maketodo.py --no-strict | sort -R | head -n10 > build/todo.txt.tmp
	mv build/todo.txt.tmp build/todo.txt


# XXX: conider moving to script
run:
	\
	    +set -ex; \
        while \
            make clean; \
            make build/todo.txt || exit 1; \
            test -s build/todo.txt; \
        do \
            if make database; then \
                make pushdb; \
            fi; \
        done; \
        true
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb run clean


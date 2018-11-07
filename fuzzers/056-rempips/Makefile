
N := 10
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_int_l.segbits $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_int_r.segbits $(addsuffix /segdata_int_r.txt,$(SPECIMENS))

pushdb:
	${XRAY_DBFIXUP} --db-dir . --clb-int
	${XRAY_MERGEDB} int_l seg_int_l.segbits
	${XRAY_MERGEDB} int_r seg_int_r.segbits

$(SPECIMENS_OK): todo.txt
	bash generate.sh $(subst /OK,,$@)
	touch $@

todo.txt:
	vivado -mode batch -source piplist.tcl
	python3 maketodo.py | sort -R | head -n10 > todo.txt

run:
	+set -ex; while make clean; make todo.txt; test -s todo.txt; do if make database; then make pushdb; fi; done; true
	touch run.ok

clean:
	rm -rf .Xil/ .cache/ filtered_seg_int_[lr].segbits run.ok
	rm -rf todo.txt vivado* piplist/ piplist.dcp pattern_[lr].txt pips_int_[lr].txt
	rm -rf specimen_[0-9][0-9][0-9]/ seg_int_[lr].segbits

.PHONY: database pushdb run clean



N := 10
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 5 -M 15 -o segbits_int_l.db $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o segbits_int_r.db $(addsuffix /segdata_int_r.txt,$(SPECIMENS))

pushdb:
	${XRAY_DBFIXUP} --db-root . --clb-int
	${XRAY_MERGEDB} int_l segbits_int_l.db
	${XRAY_MERGEDB} int_r segbits_int_r.db

$(SPECIMENS_OK): todo.txt
	bash generate.sh $(subst /OK,,$@)
	touch $@

todo.txt:
	echo "INT_L.GFAN0.GND_WIRE" >  todo.txt
	echo "INT_L.GFAN1.GND_WIRE" >> todo.txt
	echo "INT_R.GFAN0.GND_WIRE" >> todo.txt
	echo "INT_R.GFAN1.GND_WIRE" >> todo.txt

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf .Xil/ .cache/ filtered_seg_int_[lr].db run.ok
	rm -rf todo.txt vivado* pattern_[lr].txt pips_int_[lr].txt
	rm -rf specimen_[0-9][0-9][0-9]/ segbits_int_[lr].db mask_clbl[lm]_[lr].segbits

.PHONY: database pushdb run clean


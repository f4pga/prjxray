
N := 100
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	grep '^INT_L\.' todo.txt | sed 's/INT_L\./^INT./; s/$$/ ./;' > pattern_l.txt
	grep '^INT_R\.' todo.txt | sed 's/INT_R\./^INT./; s/$$/ ./;' > pattern_r.txt
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_int_l.segbits $(addsuffix /segdata_clbl[lm]_l_[0-9][0-9][0-9].txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_int_r.segbits $(addsuffix /segdata_clbl[lm]_r_[0-9][0-9][0-9].txt,$(SPECIMENS))
	grep -f pattern_l.txt seg_int_l.segbits > filtered_seg_int_l.segbits
	grep -f pattern_l.txt seg_int_r.segbits > filtered_seg_int_r.segbits

pushdb:
	${XRAY_MERGEDB} int_l filtered_seg_int_l.segbits
	${XRAY_MERGEDB} int_r filtered_seg_int_r.segbits
	${XRAY_DBFIXUP}

$(SPECIMENS_OK): todo.txt
	bash generate.sh $(subst /OK,,$@)
	touch $@

todo.txt:
	vivado -mode batch -source piplist.tcl
	python3 maketodo.py > todo.txt

clean:
	rm -rf .Xil/ filtered_seg_int_[lr].segbits
	rm -rf todo.txt vivado* piplist/ piplist.dcp pattern_[lr].txt pips_int_[lr].txt
	rm -rf specimen_[0-9][0-9][0-9]/ seg_int_[lr].segbits mask_clbl[lm]_[lr].segbits

.PHONY: database pushdb clean


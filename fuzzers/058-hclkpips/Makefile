
N := 2
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o seg_hclk_l.segbits $(addsuffix /segdata_hclk_l_design_*.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -o seg_hclk_r.segbits $(addsuffix /segdata_hclk_r_design_*.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} mask_hclk_l.segbits $(addsuffix /segdata_hclk_l_design_*.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} mask_hclk_r.segbits $(addsuffix /segdata_hclk_r_design_*.txt,$(SPECIMENS))
	grep CK_INOUT seg_hclk_l.segbits | sed 's, .*, always,' > ppips_hclk_l.txt
	grep CK_INOUT seg_hclk_r.segbits | sed 's, .*, always,' > ppips_hclk_r.txt

pushdb:
	${XRAY_MERGEDB} hclk_l seg_hclk_l.segbits
	${XRAY_MERGEDB} hclk_r seg_hclk_r.segbits
	${XRAY_MERGEDB} mask_hclk_l mask_hclk_l.segbits
	${XRAY_MERGEDB} mask_hclk_r mask_hclk_r.segbits
	cp ppips_hclk_l.txt  ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_hclk_l.db
	cp ppips_hclk_r.txt  ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_hclk_r.db
	${XRAY_DBFIXUP}

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	+set -ex; make clean; make; make pushdb

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_hclk_[lr].segbits mask_hclk_[lr].segbits ppips_hclk_[lr].txt

.PHONY: database pushdb run clean



N := 2
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_hclk_l.db $(addsuffix /segdata_hclk_l_design_*.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -o build/segbits_hclk_r.db $(addsuffix /segdata_hclk_r_design_*.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} mask_hclk_l.db $(addsuffix /segdata_hclk_l_design_*.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} mask_hclk_r.db $(addsuffix /segdata_hclk_r_design_*.txt,$(SPECIMENS))
	grep CK_INOUT build/segbits_hclk_l.db | sed 's, .*, always,' > build/ppips_hclk_l.txt
	grep CK_INOUT build/segbits_hclk_r.db | sed 's, .*, always,' > build/ppips_hclk_r.txt

pushdb:
	${XRAY_DBFIXUP} --db-root . --clb-int
	${XRAY_MERGEDB} hclk_l build/segbits_hclk_l.db
	${XRAY_MERGEDB} hclk_r build/segbits_hclk_r.db
	${XRAY_MERGEDB} mask_hclk_l build/mask_hclk_l.db
	${XRAY_MERGEDB} mask_hclk_r build/mask_hclk_r.db
	cp build/ppips_hclk_l.txt  ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_hclk_l.db
	cp build/ppips_hclk_r.txt  ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_hclk_r.db

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb

clean:
	rm -rf build run.ok

.PHONY: database pushdb run clean


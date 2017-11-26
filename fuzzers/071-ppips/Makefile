
N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	cp specimen_001/ppips_clblm_l.txt .
	cp specimen_001/ppips_clblm_r.txt .
	cp specimen_001/ppips_clbll_l.txt .
	cp specimen_001/ppips_clbll_r.txt .
	cp specimen_001/ppips_int_l.txt .
	cp specimen_001/ppips_int_r.txt .

pushdb:
	cp ppips_clblm_l.txt ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_clblm_l.db
	cp ppips_clblm_r.txt ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_clblm_r.db
	cp ppips_clbll_l.txt ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_clbll_l.db
	cp ppips_clbll_r.txt ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_clbll_r.db
	cp ppips_int_l.txt   ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_int_l.db
	cp ppips_int_r.txt   ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/ppips_int_r.db

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ ppips_clbl[ml]_[lr].txt ppips_int_[lr].txt

.PHONY: database pushdb clean


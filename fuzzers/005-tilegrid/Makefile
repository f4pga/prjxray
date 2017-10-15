
N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database.txt: $(SPECIMENS_OK)
	: ../../tools/segmatch -o database.txt \
		$(addsuffix /segdata_0.txt,$(SPECIMENS)) \
		$(addsuffix /segdata_1.txt,$(SPECIMENS)) \
		$(addsuffix /segdata_2.txt,$(SPECIMENS))

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf $(SPECIMENS)

.PHONY: clean


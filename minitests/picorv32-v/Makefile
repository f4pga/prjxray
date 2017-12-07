N := 3
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

all:
	bash runme.sh

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clblx.segbits vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit design.txt .Xil

.PHONY: database pushdb clean


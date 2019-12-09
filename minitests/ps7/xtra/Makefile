.PHONY: all clean

all: ps7.v

clean:
	rm -rf ps7.v
	rm -rf ps7.csv
	rm -rf *.xml
	rm -rf *.log
	rm -rf .Xil

ps7.csv: dump_ps7.tcl
	$(XRAY_VIVADO) -mode batch -source dump_ps7.tcl -nojournal -log $(basename $@).log

ps7.v: ps7.csv make_cell.py
	python3 make_cell.py $<

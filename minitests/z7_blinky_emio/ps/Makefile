.PHONY: all clean

all: firmware run

clean:
	rm -rf *.elf
	rm -rf *.o

firmware:
	arm-linux-gnueabihf-as -o blink.o blink.s
	arm-linux-gnueabihf-ld -o blink.elf -T blink.ld blink.o

run: blink.elf
	xsct blink.tcl

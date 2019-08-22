#!/usr/bin/env python3
import random

def main():

    template = """
`default_nettype none

// ============================================================================

module rom
(
input  wire CLK,
input  wire RST,

input  wire RD,
output wire [{rom_width_minus_one}:0] O
);

// ============================================================================

reg [{rom_width_minus_one}:0] rom[0:{rom_size_minus_one}];

initial begin
{rom_data}
end

reg [{rom_width_minus_one}:0] dat;
reg [{rom_size_bits_minus_one}:0] adr;

always @(posedge CLK)
  if (RST)     adr <= 0;
  else if (RD) adr <= adr + 1;

always @(posedge CLK)
  if (RD) dat <= rom[adr];

assign O = dat;

// ============================================================================

endmodule
"""

    rom_size_bits = 5
    rom_size = 2 ** rom_size_bits
    rom_width = 8

    rom_data = [random.randint(0, 2 ** rom_width - 1) for i in range(rom_size)]

#    rom_data = []
#    for i in range(rom_size // 2):
#        rom_data.extend([0x00, 0xFF])

    rom_data = "\n".join(["  rom[%4d] <= %d'd%d;" % (i, rom_width, d) for i, d in enumerate(rom_data)])

    print(template.format(
        rom_size_bits_minus_one=rom_size_bits - 1,
        rom_size_minus_one=rom_size - 1,
        rom_width_minus_one=rom_width - 1,
        rom_data=rom_data
    ))

if __name__ == "__main__":
    main()


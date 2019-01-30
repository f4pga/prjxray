import os
import random
import json
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog


def gen_bram36():
    for tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['RAMBFIFO36E1']):
        yield tile_name, site_name


RAM_EXTENSION_OPTS = [
    "NONE",
    "LOWER",
    "UPPER",
]


def main():
    print('''
module top();
    ''')

    params = []
    for tile_name, site_name in gen_bram36():
        ram_extension_a = random.choice(RAM_EXTENSION_OPTS)
        ram_extension_b = random.choice(RAM_EXTENSION_OPTS)

        print(
            '''
            (* KEEP, DONT_TOUCH, LOC = "{site}" *)
            RAMB36E1 #(
                .READ_WIDTH_A(1),
                .WRITE_WIDTH_A(1),
                .READ_WIDTH_B(1),
                .WRITE_WIDTH_B(1),
                .RAM_EXTENSION_A({ram_extension_a}),
                .RAM_EXTENSION_B({ram_extension_b})
                ) bram_{site} (
                    .CLKARDCLK(),
                    .CLKBWRCLK(),
                    .ENARDEN(),
                    .ENBWREN(),
                    .REGCEAREGCE(),
                    .REGCEB(),
                    .RSTRAMARSTRAM(),
                    .RSTRAMB(),
                    .RSTREGARSTREG(),
                    .RSTREGB(),
                    .ADDRARDADDR(),
                    .ADDRBWRADDR(),
                    .DIADI(),
                    .DIBDI(),
                    .DIPADIP(),
                    .DIPBDIP(),
                    .WEA(),
                    .WEBWE(),
                    .DOADO(),
                    .DOBDO(),
                    .DOPADOP(),
                    .DOPBDOP());
            '''.format(
                site=site_name,
                ram_extension_a=verilog.quote(ram_extension_a),
                ram_extension_b=verilog.quote(ram_extension_b),
            ))

        params.append(
            {
                'tile': tile_name,
                'site': site_name,
                'RAM_EXTENSION_A': ram_extension_a,
                'RAM_EXTENSION_B': ram_extension_b,
            })

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params, f, indent=2)


if __name__ == '__main__':
    main()
